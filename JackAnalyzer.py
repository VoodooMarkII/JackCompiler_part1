import JackTokenizer
import CompilationEngine

class JackAnalyzer:
    def __init__(self,input_filename):
        if input_filename.split('.')[1] =='jack':
            self.input_filename=input_filename
            self.tokenizer_output_filename=self.input_filename.split('.')[0]+'T.xml'
            self.final_output_filename=self.input_filename.split('.')[0]+'.xml'
        else:
            raise IOError('Error input file type.')

    def run(self):
        with open(self.input_filename) as in_f:
            with open(self.tokenizer_output_filename,'w') as out_f:
                jt = JackTokenizer.JackTokenizer(in_f,out_f)
                while jt.has_more_tokens():
                    token_type=jt.token_type()
                    if token_type == 'KEYWORD':
                        jt.keyword()
                    elif token_type =='SYMBOL':
                        jt.symbol()
                    elif token_type == 'IDENTIFIER':
                        jt.identifier()
                    elif token_type == 'INT_CONST':
                        jt.int_val()
                    elif token_type == 'STRING_CONST':
                        jt.string_val()
                    jt.advance()
                jt.save_xml()

        with open(self.final_output_filename,'w')as out_f:
            ce=CompilationEngine.CompilationEngine(self.tokenizer_output_filename,out_f)



if __name__ =='__main__':
    ja=JackAnalyzer('Main.jack')
    ja.run()