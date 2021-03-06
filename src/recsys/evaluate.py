import json
import logging

from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def generate_splits(filepath, random_state, train_size=0.8):
    """Generate a train and test split from raw data file

    Args:
        filepath (`str`): Path to the JSON file
        train_size (float, optional): Relative size of train set.
        Defaults to 0.8.

    Returns:
        JSON, JSON: Train and test sets as a JSON, or a Python `dict` object
    """
    try:
        with open(filepath, "r") as f:
            obj = json.load(f)
            logger.debug("Opened file at %s", filepath)
    except json.JSONDecodeError:
        logger.error("invalid file supplied at %s, exiting eval", filepath)
        return None

    train, test = train_test_split(
        obj, train_size=train_size, shuffle=True, random_state=random_state
    )
    logger.info(
        "Created train set of size %i and \
        test set of size %i, train size %f",
        len(train),
        len(test),
        train_size,
    )

    return train, test


def get_accuracy(trained_model, test_list):
    """Evaluate a trained model

    Args:
        trained_model (any): Generic model object
        test_list (`list`): Test set as a list

    Returns:
        float: Correct classification rate
    """
    try:
        cleantest = [(i["ingredients"], i["cuisine"]) for i in test_list]
    except KeyError:
        logger.error("Test set contains corrupted values")
        return None

    def evaluator(x):
        """Compare label to prediction"""
        return x[1] in list(trained_model.predict(x[0]).index)

    # Return percentage of sets of predictions that matched
    # the label within set
    try:
        acc = sum(list(map(evaluator, cleantest))) / len(cleantest)
    except ZeroDivisionError:
        logger.error("Supplied empty training set, exiting")
        return None

    return acc
