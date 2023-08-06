
from codetext.utils import parse_code
from codetext.parser import GoParser, PhpParser, RubyParser, JavaParser, JavascriptParser, \
    PythonParser, CppParser, CsharpParser, RustParser
from codetext.parser.language_parser import get_node_text
import os
from .codeSyncNet import CodeSyncNet
import torch

SUPPORTED_LANGUAGE = ['python', 'java', 'javascript', 'ruby', 'go', 'c', 'c++', 'c#', 'php', 'rust']

def get_language_parser(language):
    if language == 'python':
        return PythonParser
    if language == 'java':
        return JavaParser
    if language == 'javascript':
        return JavascriptParser
    if language == 'ruby':
        return RubyParser
    if language == 'go':
        return GoParser
    if language == 'c':
        return CppParser
    if language == 'cpp':
        return CppParser
    if language == 'c++':
        return CppParser
    if language == 'c_sharp':
        return CsharpParser
    if language == 'c#':
        return CsharpParser
    if language == 'php':
        return PhpParser
    if language == 'rust':
        return RustParser
    


def _inference(codes, docstrings, model):
    results = []
    sou_ids = []
    tar_ids = []
    for code, docstring in zip(codes, docstrings):
        source_ids, target_ids = model.tokenize(code, docstring)
        sou_ids.append(source_ids)
        tar_ids.append(target_ids)
    
    sou_ids = torch.stack(sou_ids)
    tar_ids = torch.stack(tar_ids)
    with torch.no_grad():
        output_labels, pred_texts = model.model(sou_ids,target_ids=tar_ids, stage='inference')   
        for out_label, docs, pred_text in zip(output_labels, docstrings, pred_texts):
            if out_label == 0 or docs == '':
                result = "UNMATCH!\n\t"
                t = pred_text[0].cpu().numpy()
                t = list(t)
                if 0 in t:
                    t = t[:t.index(0)]
                output_text = model.tokenizer.decode(t,clean_up_tokenization_spaces=False)
                result += "Recommended docstring: "+ output_text
            else:
                result = "MATCH!"
            results.append(result)
    return results

def get_comment(parser, raw_code):
    comments = parser.get_comment_node(raw_code)
    first_comment = comments[0]
    first_comment = get_node_text(first_comment)
    return first_comment

def inference(input_file_path=None, raw_code=None, language=None, output_file_path=None):
    assert raw_code is not None or input_file_path is not None, f"Expect your code function or file path to predict"
    assert language is not None, f"Expect the language of your code"
    model = CodeSyncNet()
    Parser = get_language_parser(language)
    if input_file_path is not None:
        assert os.path.isfile(input_file_path), f"Expect the file path"
        raw_code = ""
        with open(input_file_path, 'r') as f:
            for line in f:
                raw_code += line

    root = parse_code(raw_code, 'python') 
    root_node = root.root_node
    function_list = Parser.get_function_list(root_node)
    if output_file_path is None:
        output_file_path = "./out.txt"
    codes  = []
    docstrings = []
    func_names = []
    for function in function_list:
        raw_code = get_node_text(function)
        code_tree = parse_code(raw_code, 'python')
        code_tree_node = code_tree.root_node
        code_snippet = Parser.get_function_list(code_tree_node)[0]
        docstring = get_comment(Parser,code_snippet)
        metadata = Parser.get_function_metadata(code_snippet)

        code = raw_code.replace(docstring,"")
        docstring = docstring.strip('"').strip("'").strip("#")
        codes.append(code)
        docstrings.append(docstring)
        func_names.append(metadata['identifier'])

    results = _inference(codes, docstrings, model)

    if input_file_path is not None:
        with open(output_file_path, "w") as fo:
            for id in range(len(results)):
                fo.write("Your code snippet function: "+func_names[id]+"\n")
                fo.write('Results: \n')
                fo.write("\t" + results[id]+"\n")
                fo.write("--------------\n")
    else:
        for id in range(len(results)):
                print("Your code snippet function: "+func_names[id])
                print('Results: ')
                print("\t" + results[id])
                print("--------------")

if __name__ == "__main__":
    # inference(input_file_path='../../tests/test.py', language='python')
    raw_code = """
    def inject_func_as_unbound_method(class_, func, method_name=None):
        # This is actually quite simple
        if method_name is None:
            method_name = get_funcname(func)
        setattr(class_, method_name, func)
    """
    inference(raw_code=raw_code,language='python')