from evaluate import load


def test_bert_score():
    bertscore = load("bertscore")
    predictions = ["hello world", "general kenobi"]
    references = ["goodnight moon", "the sun is shining"]
    results = bertscore.compute(
        predictions=predictions,
        references=references,
        model_type="distilbert-base-uncased",
    )
    assert results["precision"][0] > 0.75
    assert results["precision"][0] > 0.55
    assert results["recall"][0] > 0.73
    assert results["f1"][0] > 0.73
