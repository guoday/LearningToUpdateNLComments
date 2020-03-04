import argparse
import copy
import json
import logging
import os
import re

from data_utils import read_examples_from_file
from eval_utils import compute_accuracy, compute_bleu, compute_meteor, write_predictions
from external_cache import get_return_type_subtokens, get_old_return_type_subtokens,\
    get_new_return_sequence, get_old_return_sequence, get_old_code, get_new_code, is_operator

def evaluate_copy(examples):
    return [ex.old_comment_tokens for ex in examples]

def evaluate_string_replace(examples):
    predictions = []
    easy_ids = []
    hard_ids = []

    for ex in examples:
        old_code = get_old_code(ex)
        new_code = get_new_code(ex)

        old_return_type_subtokens = get_old_return_type_subtokens(ex)
        new_return_type_subtokens = get_return_type_subtokens(ex)

        old_only = []
        new_only = []

        for s in old_return_type_subtokens:
            if s == '<' or s == '[':
                break
            # if s not in new_return_type_subtokens:
            old_only.append(s)
        
        for s in new_return_type_subtokens:
            if s == '<' or s == '[':
                break
            # if s not in old_return_type_subtokens:
            new_only.append(s)

        prediction = ex.old_comment_tokens.copy()
        if len(old_only) == 1 and old_only[0] in ex.old_comment_tokens:
            idx = ex.old_comment_tokens.index(old_only[0])
            prediction = prediction[:idx] + new_only + prediction[idx+1:]
        elif len(old_only) > 1:
            old_phrase = ' '.join(old_only)
            new_phrase = ' '.join(new_only)

            pred_str = ' '.join(prediction)
            if old_phrase in pred_str:
                start_idx = pred_str.index(old_phrase)
                end_idx = start_idx + len(old_phrase)
                new_pred_str = pred_str[:start_idx] + new_phrase + pred_str[end_idx:]
                new_pred_str = ' '.join(new_pred_str.split())
                prediction = new_pred_str.split(' ')
        
        predictions.append(prediction)

    return predictions

def evaluate(examples):
    references = []
    predictions = []
    easy_ids = []
    hard_ids = []

    for ex in examples:

        old_code = get_old_code(ex)
        new_code = get_new_code(ex)

        old_return_type_subtokens = get_old_return_type_subtokens(ex)
        new_return_type_subtokens = get_return_type_subtokens(ex)

        old_return_sequence = get_old_return_sequence(ex)
        new_return_sequence = get_new_return_sequence(ex)

        old_only = []
        new_only = []

        for s in old_return_type_subtokens:
            if s == '<' or s == '[':
                break
            # if s not in new_return_type_subtokens:
            old_only.append(s)
        
        for s in new_return_type_subtokens:
            if s == '<' or s == '[':
                break
            # if s not in old_return_type_subtokens:
            new_only.append(s)

        prediction = ex.old_comment_tokens.copy()
        old_phrase = ' '.join(old_only)
        new_phrase = ' '.join(new_only)
        pred_str = ' '.join(prediction)

        if len(old_only) == 1 and old_only[0] in ex.old_comment_tokens:
            idx = ex.old_comment_tokens.index(old_only[0])
            prediction = prediction[:idx] + new_only + prediction[idx+1:]
        elif len(old_only) > 1 and old_phrase in pred_str:
            start_idx = pred_str.index(old_phrase)
            end_idx = start_idx + len(old_phrase)
            new_pred_str = pred_str[:start_idx] + new_phrase + pred_str[end_idx:]
            new_pred_str = ' '.join(new_pred_str.split())
            prediction = new_pred_str.split(' ')
        else:
            if ('null' not in ex.old_comment_tokens):
                old_conds = re.findall(r'=(\s)*null', old_code)
                old_rets =rets = re.findall(r'return(\s)*null;', old_code)

                new_conds = re.findall(r'=(\s)*null', new_code)
                new_rets = re.findall(r'return(\s)*null;', new_code)

                if len(new_rets) > len(old_rets) or len(new_conds) > len(old_conds):
                    prediction.extend(['or', 'null', 'if', 'null'])
        predictions.append(prediction)

    return predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-data_path')
    parser.add_argument('--hard', action='store_true')
    parser.add_argument('--easy', action='store_true')
    args = parser.parse_args()

    if args.hard:
        test_file = 'hard_test.json'
    elif args.easy:
        test_file = 'easy_test.json'
    else:
        test_file = 'test.json'

    test_examples = read_examples_from_file(os.path.join(args.data_path, test_file))
    
    ########################################
    predictions = evaluate(test_examples)
    references = [[ex.new_comment_tokens] for ex in test_examples]

    pred_strs = [' '.join(p) for p in predictions]
    gold_strs = [ex.new_comment for ex in test_examples]

    predicted_accuracy = compute_accuracy(gold_strs, pred_strs)
    predicted_bleu = compute_bleu(references, predictions)
    predicted_meteor = compute_meteor(references, predictions)


    print('Predicted Accuracy: {}'.format(predicted_accuracy))
    print('Predicted BLEU: {}'.format(predicted_bleu))
    print('Predicted Meteor: {}\n'.format(predicted_meteor))
    write_path = os.path.join('baseline-models', args.data_path.split('/')[-1], 'rule_based.txt')
    write_predictions(pred_strs, write_path)

    ########################################
    predictions = evaluate_string_replace(test_examples)
    references = [[ex.new_comment_tokens] for ex in test_examples]

    pred_strs = [' '.join(p) for p in predictions]
    gold_strs = [ex.new_comment for ex in test_examples]

    predicted_accuracy = compute_accuracy(gold_strs, pred_strs)
    predicted_bleu = compute_bleu(references, predictions)
    predicted_meteor = compute_meteor(references, predictions)

    print('\nPredicted Accuracy: {}'.format(predicted_accuracy))
    print('Predicted BLEU: {}'.format(predicted_bleu))
    print('Predicted Meteor: {}\n'.format(predicted_meteor))

    write_path = os.path.join('baseline-models', args.data_path.split('/')[-1], 'string_replace.txt')
    write_predictions(pred_strs, write_path)

    ########################################
    
    predictions = evaluate_copy(test_examples)
    references = [[ex.new_comment_tokens] for ex in test_examples]

    pred_strs = [' '.join(p) for p in predictions]
    gold_strs = [ex.new_comment for ex in test_examples]

    predicted_accuracy = compute_accuracy(gold_strs, pred_strs)
    predicted_bleu = compute_bleu(references, predictions)
    predicted_meteor = compute_meteor(references, predictions)

    print('\nPredicted Accuracy: {}'.format(predicted_accuracy))
    print('Predicted BLEU: {}'.format(predicted_bleu))
    print('Predicted Meteor: {}\n'.format(predicted_meteor))

    write_path = os.path.join('baseline-models', args.data_path.split('/')[-1], 'copy.txt')
    write_predictions(pred_strs, write_path)