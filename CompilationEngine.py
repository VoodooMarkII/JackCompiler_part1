import xml.dom.minidom


class CompilationEngine:
    def __init__(self, input_filename, output_file=None):
        self.input_filename = input_filename
        self.output_file = output_file

        self.in_xml = xml.dom.minidom.parse(self.input_filename)
        self.input_child_node_idx = 1
        self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
        self.doc = xml.dom.minidom.Document()

        self.compile_class()
        self.__save_xml()
        pass

    def compile_class(self):
        if self.current_token.childNodes[0].nodeValue == 'class':
            class_node = self.doc.createElement('class')
            self.doc.appendChild(class_node)
            class_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                class_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
                    class_node.appendChild(self.current_token)
                    self.__idx_advance()
                    self.compile_class_var_dec(class_node)
                    self.compile_subroutine_dec(class_node)

    def compile_class_var_dec(self, class_node):
        if self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['static', 'field']:
            class_var_dec_node = self.doc.createElement('classVarDec')
            class_node.appendChild(class_var_dec_node)
            class_var_dec_node.appendChild(self.current_token)
            self.__idx_advance()

    def compile_subroutine_dec(self, class_node):
        if self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['constructor', 'function', 'method']:
            subroutine_dec_node = self.doc.createElement('subroutineDec')
            class_node.appendChild(subroutine_dec_node)
            subroutine_dec_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier' or \
                    self.current_token.childNodes[0].nodeValue in ['void', 'int', 'char', 'boolean']:
                subroutine_dec_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'identifier':
                    subroutine_dec_node.appendChild(self.current_token)
                    self.__idx_advance()
                    if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                        subroutine_dec_node.appendChild(self.current_token)
                        self.__idx_advance()
                        self.compile_parameter_list(subroutine_dec_node)
                        # advance?
                        if self.current_token.nodeName == 'symbol' and \
                                self.current_token.childNodes[0].nodeValue == ')':
                            subroutine_dec_node.appendChild(self.current_token)
                            self.__idx_advance()
                            self.compile_subroutine_body(subroutine_dec_node)

    def compile_parameter_list(self, father_node):
        if self.current_token.nodeName == 'identifier' or \
                self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
            parameter_list_node = self.doc.createElement('parameterList')
            father_node.appendChild(parameter_list_node)
            parameter_list_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier':
                parameter_list_node.appendChild(self.current_token)
                self.__idx_advance()
                while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
                    parameter_list_node.appendChild(self.current_token)
                    self.__idx_advance()
                    if self.current_token.nodeName == 'identifier' or \
                            self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
                        parameter_list_node.appendChild(self.current_token)
                        self.__idx_advance()
                        if self.current_token.nodeName == 'identifier':
                            parameter_list_node.appendChild(self.current_token)
                            self.__idx_advance()
        else:
            return

    def compile_subroutine_body(self, father_node):
        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '{':
            subroutine_body_node = self.doc.createElement('subroutineBody')
            father_node.appendChild(subroutine_body_node)
            subroutine_body_node.appendChild(self.current_token)
            self.__idx_advance()
            while self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'var':
                self.compile_var_dec(subroutine_body_node)
                self.__idx_advance()
            self.compile_statements(subroutine_body_node)

    def compile_var_dec(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'var':
            var_dec_node = self.doc.createElement('varDec')
            father_node.appendChild(var_dec_node)
            var_dec_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'identifier' or \
                    self.current_token.childNodes[0].nodeValue in ['int', 'char', 'boolean']:
                var_dec_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'identifier':
                    var_dec_node.appendChild(self.current_token)
                    self.__idx_advance()
                    while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
                        var_dec_node.appendChild(self.current_token)
                        self.__idx_advance()
                        if self.current_token.nodeName == 'identifier':
                            var_dec_node.appendChild(self.current_token)
                            self.__idx_advance()
                    if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
                        var_dec_node.appendChild(self.current_token)

    def compile_statements(self, father_node):
        statements_node = self.doc.createElement('statements')
        father_node.appendChild(statements_node)
        while self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['let', 'if', 'while', 'do']:
            if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'let':
                self.compile_let(statements_node)
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'if':
                self.compile_if()
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'while':
                self.compile_while()
            elif self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'do':
                self.compile_do()

    def compile_let(self, father_node):
        if self.current_token.nodeName == 'keyword' and self.current_token.childNodes[0].nodeValue == 'let':
            let_node = self.doc.createElement('letStatement')
            father_node.appendChild(let_node)
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("'let' expected.")

        if self.current_token.nodeName == 'identifier':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError('Identifier exprected.')

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '[':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ']':
                let_node.appendChild(self.current_token)
                self.__idx_advance()
            else:
                raise SyntaxError("']' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '=':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression(let_node)
        else:
            raise SyntaxError("'=' expected.")

        if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ';':
            let_node.appendChild(self.current_token)
            self.__idx_advance()
        else:
            raise SyntaxError("';' expected.")

    def compile_if(self):
        pass

    def compile_while(self):
        pass

    def compile_do(self):
        pass

    def compile_return(self):
        pass

    def compile_expression(self, father_node):
        expression_node = self.doc.createElement('expression')
        father_node.appendChild(expression_node)
        self.compile_term(expression_node)
        while self.current_token.nodeName == 'symbol' and \
                self.current_token.childNodes[0].nodeValue in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            expression_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_term(expression_node)

    def compile_term(self, father_node):
        term_node = self.doc.createElement('term')
        father_node.appendChild(term_node)
        if self.current_token.nodeName in ['integerConstant', 'stringConstant']:
            term_node.appendChild(self.current_token)
            self.__idx_advance()

        elif self.current_token.nodeName == 'keyword' and \
                self.current_token.childNodes[0].nodeValue in ['true', 'false', 'null', 'this']:
            term_node.appendChild(self.current_token)
            self.__idx_advance()

        # Processing varName, varName[expression] and subroutineCall
        elif self.current_token.nodeName == 'identifier':
            term_node.appendChild(self.current_token)
            self.__idx_advance()
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '[':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression(term_node)
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ']':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                else:
                    raise SyntaxError("']' expected.")

            elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression_list(term_node)
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
            elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '.':
                term_node.appendChild(self.current_token)
                self.__idx_advance()
                if self.current_token.nodeName == 'identifier':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
                    term_node.appendChild(self.current_token)
                    self.__idx_advance()
                    self.compile_expression_list(term_node)
                    if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                        term_node.appendChild(self.current_token)
                        self.__idx_advance()

        # Processing (expression)
        elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == '(':
            term_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_expression(term_node)
            if self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')':
                term_node.appendChild(self.current_token)
            else:
                raise SyntaxError("'(' expected.")

        # Processing unaryOp term
        elif self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue in ['-', '~']:
            term_node.appendChild(self.current_token)
            self.__idx_advance()
            self.compile_term(term_node)

        # Processing subroutineCall
        else:
            raise SyntaxError('Term expected.')

    def compile_expression_list(self, father_node):
        expression_list_node = self.doc.createElement('expressionList')
        father_node.appendChild(expression_list_node)
        if not (self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ')'):
            self.compile_expression(expression_list_node)
            while self.current_token.nodeName == 'symbol' and self.current_token.childNodes[0].nodeValue == ',':
                expression_list_node.appendChild(self.current_token)
                self.__idx_advance()
                self.compile_expression(expression_list_node)

    def __idx_advance(self):
        self.input_child_node_idx = self.input_child_node_idx + 1
        self.current_token = self.in_xml.documentElement.childNodes[self.input_child_node_idx]
        if not isinstance(self.current_token, xml.dom.minidom.Element):
            self.__idx_advance()

    def __save_xml(self):
        self.output_file.write(self.doc.toprettyxml(indent='  '))
