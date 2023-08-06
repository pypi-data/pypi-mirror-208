def inject_func_as_unbound_method(class_, func, method_name=None):
         #   This is actually quite simple
        if method_name is None:
            method_name = get_funcname(func)
        setattr(class_, method_name, func)

def inference(self, code, docstring):
        """
        inference file
        """
        code_ids, docstring_ids = self.tokenize(code, docstring)
        
        with torch.no_grad():
            output_label, pred_text = self.model(code_ids,target_ids=docstring_ids, stage='inference')   
            output_label = output_label[0]
        print('-----------------')
        if output_label == 0:
            print("UNMATCH!")
            pred_text = pred_text[0]
            t = pred_text[0].cpu().numpy()
            t = list(t)
            if 0 in t:
                t = t[:t.index(0)]
            output_text = self.tokenizer.decode(t,clean_up_tokenization_spaces=False)
            print("Recommended docstring: ", output_text)
        else:
            print("MATCH!")