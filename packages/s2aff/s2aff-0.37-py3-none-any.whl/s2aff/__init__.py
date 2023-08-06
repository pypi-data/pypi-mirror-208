import logging
import multiprocess
from s2aff.model import parse_ner_prediction

logger = logging.getLogger("s2aff")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
logger.addHandler(ch)


def custom_error_callback(error):
    print(f'\nS2AFF multiprocessing got error: {error}\n')

def fill_list(start, end, result, inputs, self_ror_index, self_look_for_grid_and_isni, self_no_candidates_output_text, self_pairwise_model, self_top_k_first_stage, self_pairwise_model_threshold, self_no_ror_output_text, self_pairwise_model_delta_threshold, self_number_of_top_candidates_to_return):
    # This function fills the result list with the values from start to end
    for i in range(start, end):
        counter, raw_affiliation, ner_prediction = inputs[i]
        # Do some work here
        print(
            f"\nGetting ROR candidates and reranking for: '{raw_affiliation}' ({counter + 1}/{len(raw_affiliations)})\n",
            end="\r",
        )
        main, child, address, early_candidates = parse_ner_prediction(ner_prediction, self_ror_index)
        # sometimes the affiliation strings just contain GRID or ISNI ids
        # todo: some time in the future the strings may contain ROR ids too
        if self_look_for_grid_and_isni:
            ror_from_grid = self_ror_index.extract_grid_and_map_to_ror(raw_affiliation)
            ror_from_isni = self_ror_index.extract_isni_and_map_to_ror(raw_affiliation)
            ror_from_grid_or_isni = ror_from_grid or ror_from_isni
            found_early = ror_from_grid_or_isni is not None
            if found_early:
                candidates, scores = [ror_from_grid_or_isni], [1.0]
        else:
            found_early = False
        # we don't want to rerank if we found a GRID or ISNI id
        if not found_early:
            candidates, scores = self_ror_index.get_candidates_from_main_affiliation(
                main, address, early_candidates
            )

        if len(candidates) == 0:
            output_scores_and_thresh = [self_no_candidates_output_text], [0.0]
        else:
            reranked_candidates, reranked_scores = self_pairwise_model.predict(
                raw_affiliation, candidates[: self_top_k_first_stage], scores[: self_top_k_first_stage]
            )
            # apply threshold to reranked scores
            if len(reranked_candidates) == 0:
                output_scores_and_thresh = [self_no_candidates_output_text], [0.0]
            elif len(reranked_candidates) == 1:
                if reranked_scores[0] < self_pairwise_model_threshold:
                    output_scores_and_thresh = [self_no_ror_output_text], [0.0]
                else:
                    output_scores_and_thresh = (reranked_candidates, reranked_scores)
            else:
                delta = reranked_scores[0] - reranked_scores[1]
                if (
                        reranked_scores[0] < self_pairwise_model_threshold
                        and delta < self_pairwise_model_delta_threshold
                ):
                    output_scores_and_thresh = [self_no_ror_output_text], [0.0]
                else:
                    output_scores_and_thresh = (reranked_candidates, reranked_scores)
        try:
            display_name = self_ror_index.ror_dict[output_scores_and_thresh[0][0]]["name"]
        except:
            display_name = ""

        # make a dict of outputs
        output = {
            "raw_affiliation": raw_affiliation,
            "ner_prediction": ner_prediction,
            "main_from_ner": main,
            "child_from_ner": child,
            "address_from_ner": address,
            "stage1_candidates": list(candidates[: self_number_of_top_candidates_to_return]),
            "stage1_scores": list(scores[: self_number_of_top_candidates_to_return]),
            "stage2_candidates": list(output_scores_and_thresh[0][: self_number_of_top_candidates_to_return]),
            "stage2_scores": list(output_scores_and_thresh[1][: self_number_of_top_candidates_to_return]),
            "top_candidate_display_name": display_name,
        }
        result[i] = output


class S2AFF:
    """
    The wrapper class that links a raw affiliation string to a ROR entry.

    :param ner_predictor: an instantiated NERPredictor object
    :param ror_index: an instantiated RORIndex object
    :param pairwise_model: an instantiated pairwise model with `predict` method that
        returns a list of reranked candidates and a list of reranked scores
        best we have is `PairwiseRORLightGBMReranker`
    :param top_k_first_stage: the number of top first stage RORINdex candidates to rerank
        default = 100
    :param pairwise_model_threshold: the threshold for the pairwise model,
        if the top score is below this threshold, and the difference between the top
        two scores is below the delta threshold, then there is no ROR match
        default = 0.3, found in `scripts/analyze_thresholds.ipynb`
    :param pairwise_model_delta_threshold: the delta threshold for the pairwise model
        if the difference between the top two scores is below this threshold and
        the top score is below the threshold (previous param) then there is no ROR match
        default = 0.2, found in `scripts/analyze_thresholds.ipynb`
    :param no_ror_output_text: the text to return if no ROR is found due to thereshold
        default = "NO_ROR_FOUND"
    :param no_candidates_output_text: the text to return if no candidates are found in the first stage
        default = "NO_CANDIDATES_FOUND"
    :param number_of_top_candidates_to_return: the number of top candidates to return in the second stage of the algorithm
        a convenience to reduce the total amount of data sent
        default = 5
    :param look_for_grid_and_isni: whether to look for GRID and ISNI ids in the raw affiliation string
        ff found, just returns that candidate as the only one to the subsequent step
        default = True
    """

    def __init__(
        self,
        ner_predictor,
        ror_index,
        pairwise_model,
        top_k_first_stage=20,
        pairwise_model_threshold=0.3,
        pairwise_model_delta_threshold=0.2,
        no_ror_output_text="NO_ROR_FOUND",
        no_candidates_output_text="NO_CANDIDATES_FOUND",
        number_of_top_candidates_to_return=1,
        look_for_grid_and_isni=True,
    ):
        self.ner_predictor = ner_predictor
        self.ror_index = ror_index
        self.pairwise_model = pairwise_model
        self.top_k_first_stage = top_k_first_stage
        self.pairwise_model_threshold = pairwise_model_threshold
        self.pairwise_model_delta_threshold = pairwise_model_delta_threshold
        self.no_ror_output_text = no_ror_output_text
        self.no_candidates_output_text = no_candidates_output_text
        self.number_of_top_candidates_to_return = number_of_top_candidates_to_return
        self.look_for_grid_and_isni = True

    def predict(self, raw_affiliations):
        """Predict function for raw affiliation strings

        :param raw_affiliations: a list of raw affiliation strings

        :return: a list of dictionaries with the following keys:
            "raw_affiliation": raw affiliation string
            "ner_prediction": raw NER prediction
            "main_from_ner": main institute portion of the raw_affiliation extracted from NER prediction
            "child_from_ner": child institute (if any) portion of the raw_affiliation extracted from NER prediction
            "address_from_ner": address portion (if any) of the raw_affiliation extracted from NER prediction
            "stage1_candidates": top candidates from the RORIndex
            "stage1_scores": scores of the above candidates
            "stage2_candidates": top candidates from the pairwise model
            "stage2_scores": scores of the above candidates
        """
        # if we get a single string, we should make a list of out of it
        if isinstance(raw_affiliations, str):
            raw_affiliations = [raw_affiliations]

        print("Getting NER predictions in bulk...")
        ner_predictions = self.ner_predictor.predict(raw_affiliations)
        print("Done")

        inputs_ = []
        for counter, (raw_affiliation, ner_prediction) in enumerate(zip(raw_affiliations, ner_predictions)):
            inputs_.append((counter, raw_affiliation, ner_prediction))

        length = len(raw_affiliations)
        result_ = [None] * length

        # Set up the number of processes to use
        num_processes = multiprocess.cpu_count()

        # Split the list into equal chunks for each process
        chunk_size = length // num_processes
        chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_processes)]
        chunks[-1] = (chunks[-1][0], length)  # Make sure the last chunk goes all the way to the end
        print(f"\nCHUNKS: {chunks}\n")

        # Create a pool of processes to fill the list
        pool = multiprocess.Pool(processes=num_processes)

        # Fill the list using multiple processes
        for chunk in chunks:
            pool.apply_async(fill_list, args=(chunk[0], chunk[1], result_, inputs_, self.ror_index, self.look_for_grid_and_isni, self.no_candidates_output_text, self.pairwise_model, self.top_k_first_stage, self.pairwise_model_threshold, self.no_ror_output_text, self.pairwise_model_delta_threshold, self.number_of_top_candidates_to_return), error_callback=custom_error_callback)

        # Wait for all processes to finish
        pool.close()
        pool.join()

        # The result list should now be fully populated
        return result_
