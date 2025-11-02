'''
Lexical Analyzer
Compilers - Group 05
Students:
320206102
316255819
423031180
320117174
320340312
'''


import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font
import os

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"

class LexicalAnalyzer:
    def __init__(self):
        # Keywords
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'inline',
            'int', 'long', 'register', 'restrict', 'return', 'short', 'signed', 'sizeof',
            'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
            'volatile', 'while'
        }

        
        # Operators
        self.operators = {
            '=', '+', '-', '*', '/', '%', '++', '--',
            '==', '!=', '<', '>', '<=', '>=',
            '&&', '||', '!',
            '&', '|', '^', '~', '<<', '>>',
            '+=', '-=', '*=', '/=', '%='
        }
        
        # Punctuators
        self.punctuators = {
            '(', ')', '{', '}', '[', ']',
            ';', ',', '.', ':', '#'
        }
        
        # Special symbols (for quotes and escape)
        self.special_symbols = {
            '"', "'", '\\'
        }
        
        # Regex patterns for tokens
        self.token_patterns = [
            # String literals
            ('STRING_LITERAL', r'"([^"\\]|\\.)*"'),
            ('CHAR_LITERAL', r"'([^'\\]|\\.)'"),

            # Numbers
            ('FLOAT_CONSTANT', r'\d+\.\d*([eE][+-]?\d+)?'),
            ('INT_CONSTANT', r'\d+'),

            # Identifiers and keywords (including accents/tildes)
            ('IDENTIFIER', r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ_][a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9_]*'),

            # Comments (single-line made flexible, multi-line handled with DOTALL)
            ('COMMENT_SINGLE', r'//\s*[^\n]*'),
            ('COMMENT_MULTI', r'/\*.*?\*/'),

            # Operators (ordered by descending length to avoid conflicts)
            ('OPERATOR', r'(\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|\+=|-=|\*=|/=|%=|[+\-*/%=<>&|^~!])'),

            # Punctuators
            ('PUNCTUATOR', r'[(){}\[\];,.:#]'),

            # Special symbols (quotes and escape)
            ('SPECIAL_SYMBOL', r'["\'\\]'),

            # Whitespace (will be ignored)
            ('WHITESPACE', r'[ \t]+'),

            # Newline (we will ignore this token too)
            ('NEWLINE', r'\n'),
        ]

        # Compile patterns (enable DOTALL only for multi-line comments)
        self.compiled_patterns = []
        for name, pattern in self.token_patterns:
            if name == 'COMMENT_MULTI':
                self.compiled_patterns.append((name, re.compile(pattern, re.DOTALL)))
            else:
                self.compiled_patterns.append((name, re.compile(pattern)))


    def tokenize(self, text):
        tokens = []
        pos = 0
        line = 1
        column = 1
        length = len(text)

        # Tokens we want to skip entirely
        ignore_types = {'WHITESPACE', 'COMMENT_SINGLE', 'COMMENT_MULTI', 'NEWLINE'}

        while pos < length:
            match_found = False

            for token_type, pattern in self.compiled_patterns:
                match = pattern.match(text, pos)
                if not match:
                    continue

                value = match.group(0)
                tt = token_type  # local copy so we don't mutate the pattern name

                # classify identifiers that are keywords
                if tt == 'IDENTIFIER' and value in self.keywords:
                    tt = 'KEYWORD'

                # add token unless it's in the ignore set
                if tt not in ignore_types:
                    if tt == 'PUNCTUATOR' or (tt == 'SPECIAL_SYMBOL' and value in self.punctuators):
                        tokens.append(Token('PUNCTUATOR', value, line, column))
                    else:
                        tokens.append(Token(tt, value, line, column))

                # advance pos and update line/column
                newlines = value.count('\n')
                if newlines:
                    line += newlines
                    last_nl = value.rfind('\n')
                    # column after the last newline: number of chars after it
                    column = len(value) - last_nl
                else:
                    column += len(value)

                pos = match.end()
                match_found = True
                break

            if not match_found:
                # Unrecognized char -> produce UNKNOWN token and advance
                ch = text[pos]
                tokens.append(Token('UNKNOWN', ch, line, column))
                if ch == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                pos += 1

        return tokens

    
    def classify_tokens(self, tokens):
        """Classify tokens into categories"""
        classification = {
            'keywords': [],
            'identifiers': [],
            'punctuations': [],
            'operators': [],
            'constants': [],
            'literals': []
        }
        
        for token in tokens:
            if token.type == 'KEYWORD':
                classification['keywords'].append(token.value)
            elif token.type == 'IDENTIFIER':
                classification['identifiers'].append(token.value)
            elif token.type == 'PUNCTUATOR':
                classification['punctuations'].append(token.value)
            elif token.type == 'OPERATOR':
                classification['operators'].append(token.value)
            elif token.type in ['INT_CONSTANT', 'FLOAT_CONSTANT']:
                classification['constants'].append(token.value)
            elif token.type in ['STRING_LITERAL', 'CHAR_LITERAL']:
                classification['literals'].append(token.value)
        
        return classification

# class CFGModel:
#     """
#     Basic CFG model for variable declarations with right recursion
#     and left factorization.
    
#     Grammar:
#     S -> declaration
#     declaration -> type identifier_list ';'
#     identifier_list -> identifier identifier_list'
#     identifier_list' -> ',' identifier identifier_list' | ε
#     type -> 'int' | 'float' | 'double' | 'char' | 'string'
#     identifier -> LETTER (LETTER | DIGIT)*
    
#     Example: int x, y, z;
#     """
    
#     def __init__(self):
#         self.grammar = {
#             'S': ['declaration'],
#             'declaration': ['type identifier_list ;'],
#             'identifier_list': ['identifier identifier_list_prime'],
#             'identifier_list_prime': [', identifier identifier_list_prime', 'ε'],
#             'type': ['int', 'float', 'double', 'char', 'string'],
#             'identifier': ['LETTER (LETTER | DIGIT)*']
#         }
    
#     def get_grammar_text(self):
#         text = "CONTEXT-FREE GRAMMAR (CFG)\n"
#         text += "Variable declarations with right recursion\n"
#         text += "=" * 60 + "\n\n"
        
#         for non_terminal, productions in self.grammar.items():
#             text += f"{non_terminal} -> {productions[0]}\n"
#             for production in productions[1:]:
#                 text += f"{' ' * (len(non_terminal) + 3)}| {production}\n"
        
#         text += "\nApplied features:\n"
#         text += "✓ Right recursion in 'identifier_list_prime'\n"
#         text += "✓ Left factorization in 'identifier_list'\n"
#         text += "✓ Epsilon production (ε) to terminate recursion\n"
        
#         return text

class LexicalAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lexical Analyzer - Compilers")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f1419")
        
        # Initialize analyzer and CFG
        self.analyzer = LexicalAnalyzer()
        # self.cfg = CFGModel()
        
        # Setup theme
        self.setup_theme()
        
        # Setup interface
        self.setup_ui()
        
        # Create sample file
        self.create_sample_file()
    
    def setup_theme(self):
        # Modern blue theme colors
        self.colors = {
            'bg_primary': '#d9e6f2',      # Light bluish gray (main app background, a bit darker)
            'bg_secondary': '#c0d4e8',    # Medium-light blue (panels / code background, darker for contrast)
            'bg_tertiary': '#a9c3db',     # Mid blue-gray (interactive elements, buttons, hovers)
            'accent': '#2b6cb0',          # Calm medium blue (accents)
            'accent_hover': '#2c5282',    # Deeper muted blue (hover)
            'text_primary': '#1a202c',    # Almost black-gray (primary text)
            'text_secondary': '#2d3748',  # Dark gray-blue (secondary text)
            'success': '#2f855a',         # Balanced green (success)
            'warning': '#b7791f',         # Warm golden brown (warning)
            'error': '#c53030'            # Softer deep red (error)
        }



        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Buttons
        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent_hover'])])
        
        # Frame
        style.configure('Modern.TFrame',
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['bg_tertiary'])
        
        # Notebook (tabs)
        style.configure('Modern.TNotebook',
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_secondary'],
                       padding=[20, 10],
                       font=('Segoe UI', 10))
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['accent']),
                           ('active', self.colors['accent_hover'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
    
    def setup_ui(self):
        # Header
        self.create_header()
        
        # Main content with tabs
        self.create_main_content()
    
    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Main title
        title_label = tk.Label(header_frame, 
                              text="🔍 Lexical Analyzer",
                              font=('Segoe UI', 24, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_secondary'])
        title_label.pack(side='left', padx=30, pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Compilers - Token Analysis",
                                 font=('Segoe UI', 12),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_secondary'])
        subtitle_label.pack(side='left', padx=(0, 30), pady=(30, 10))
    
    def create_main_content(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Tab 1: Code editor
        self.create_editor_tab()
        
        # Tab 2: Token analysis
        self.create_analysis_tab()
        
        # Tab 3: Token classification
        self.create_classification_tab()
        
        # Tab 4: CFG Grammar
        # self.create_grammar_tab()
    
    def create_editor_tab(self):
        editor_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(editor_frame, text="📝 Code Editor")
        
        # Frame for buttons
        button_frame = tk.Frame(editor_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        # Action buttons
        ttk.Button(button_frame, text="📁 Open File", 
                  command=self.load_file, 
                  style='Modern.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame, text="📄 Example", 
                  command=self.load_sample, 
                  style='Modern.TButton').pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="🗑️ Clear", 
                  command=self.clear_editor, 
                  style='Modern.TButton').pack(side='left', padx=10)
        
        ttk.Button(button_frame, text="🔍 Analyze", 
                  command=self.analyze_code, 
                  style='Modern.TButton').pack(side='right', padx=(10, 0))
        
        # Text editor with line numbers
        editor_container = tk.Frame(editor_frame, bg=self.colors['bg_secondary'])
        editor_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Frame for line numbers
        line_frame = tk.Frame(editor_container, bg=self.colors['bg_tertiary'], width=50)
        line_frame.pack(side='left', fill='y')
        line_frame.pack_propagate(False)
        
        self.line_numbers = tk.Text(line_frame,
                                   width=4,
                                   padx=5,
                                   pady=10,
                                   bg=self.colors['bg_tertiary'],
                                   fg=self.colors['text_secondary'],
                                   font=('Consolas', 11),
                                   state='disabled',
                                   wrap='none',
                                   border=0,
                                   highlightthickness=0)
        self.line_numbers.pack(fill='both', expand=True)
        
        # Main editor
        self.code_editor = scrolledtext.ScrolledText(editor_container,
                                                    font=('Consolas', 11),
                                                    bg=self.colors['bg_primary'],
                                                    fg=self.colors['text_primary'],
                                                    insertbackground=self.colors['accent'],
                                                    selectbackground=self.colors['accent'],
                                                    selectforeground='white',
                                                    wrap='none',
                                                    border=0,
                                                    highlightthickness=1,
                                                    highlightcolor=self.colors['accent'],
                                                    highlightbackground=self.colors['bg_tertiary'])
        self.code_editor.pack(side='right', fill='both', expand=True)
        
        # Synchronize scroll and update line numbers
        self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<Button-1>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.sync_scroll)
        
        # Initial line numbers
        self.update_line_numbers()
    
    def create_analysis_tab(self):
        analysis_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(analysis_frame, text="📊 Token Analysis")
        
        # Upper frame for statistics
        stats_frame = tk.Frame(analysis_frame, bg=self.colors['bg_secondary'], height=100)
        stats_frame.pack(fill='x', padx=20, pady=20)
        stats_frame.pack_propagate(False)
        
        # Statistics labels
        self.total_tokens_label = tk.Label(stats_frame,
                                          text="Total Tokens: 0",
                                          font=('Segoe UI', 14, 'bold'),
                                          fg=self.colors['accent'],
                                          bg=self.colors['bg_secondary'])
        self.total_tokens_label.pack(side='left', padx=30, pady=30)
        
        self.analysis_status = tk.Label(stats_frame,
                                       text="Status: Ready for analysis",
                                       font=('Segoe UI', 12),
                                       fg=self.colors['text_secondary'],
                                       bg=self.colors['bg_secondary'])
        self.analysis_status.pack(side='left', padx=30, pady=30)
        
        # Token table
        table_frame = tk.Frame(analysis_frame, bg=self.colors['bg_secondary'])
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Treeview to show tokens
        columns = ('Type', 'Value', 'Line', 'Column')
        self.token_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                      yscrollcommand=v_scrollbar.set,
                                      xscrollcommand=h_scrollbar.set,
                                      height=15)
        
        # Configure columns
        for col in columns:
            self.token_tree.heading(col, text=col)
            self.token_tree.column(col, width=150, anchor='center')
        
        self.token_tree.pack(fill='both', expand=True)
        
        # Connect scrollbars
        v_scrollbar.config(command=self.token_tree.yview)
        h_scrollbar.config(command=self.token_tree.xview)
        
        # Configure alternating colors
        self.token_tree.tag_configure('oddrow', background=self.colors['bg_tertiary'])
        self.token_tree.tag_configure('evenrow', background=self.colors['bg_primary'])
    
    def create_classification_tab(self):
        classification_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(classification_frame, text="🏷️ Token Classification")
        
        # Main container with scrollbar
        main_container = tk.Frame(classification_frame, bg=self.colors['bg_secondary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollable text area
        self.classification_text = scrolledtext.ScrolledText(main_container,
                                                           font=('Consolas', 11),
                                                           bg=self.colors['bg_primary'],
                                                           fg=self.colors['text_primary'],
                                                           wrap='word',
                                                           state='disabled',
                                                           border=0,
                                                           highlightthickness=1,
                                                           highlightcolor=self.colors['accent'],
                                                           highlightbackground=self.colors['bg_tertiary'])
        self.classification_text.pack(fill='both', expand=True)
    
    # def create_grammar_tab(self):
    #     grammar_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
    #     self.notebook.add(grammar_frame, text="📚 CFG Grammar")
        
    #     # Text area for grammar
    #     self.grammar_text = scrolledtext.ScrolledText(grammar_frame,
    #                                                  font=('Consolas', 11),
    #                                                  bg=self.colors['bg_primary'],
    #                                                  fg=self.colors['text_primary'],
    #                                                  wrap='word',
    #                                                  state='disabled',
    #                                                  border=0,
    #                                                  highlightthickness=1,
    #                                                  highlightcolor=self.colors['accent'],
    #                                                  highlightbackground=self.colors['bg_tertiary'])
    #     self.grammar_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Load grammar
        # self.load_grammar()
    
    def update_line_numbers(self, event=None):
        line_numbers_text = ""
        lines = int(self.code_editor.index('end-1c').split('.')[0])
        for i in range(1, lines + 1):
            line_numbers_text += f"{i:>3}\n"
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
    
    def sync_scroll(self, event=None):
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])
    
    def create_sample_file(self):
        """Create sample file if it doesn't exist"""
        sample_content = '''/* This is a wonderful example of the 
lexical analyzer's functions. 
Greetings and blessings! */

int main() {
    // Variable declarations
    int x, y, z;
    float pi = 3.14159;
    char letter = 'A';
    char message[] = "The result is %d \\n"; 
    bool flag = true;

    // Arithmetic operations
    x = 10;
    y = 20;
    z = x + y * 2;

    /* Multi-line comment
       with more information */
    
    // Control structures
    if (x > 0) {
        printf(message, z);   // Print the computed result
    } else if (x < 0) {
        printf("x is negative \\n");
    } else {
        printf("x is zero \\n");
    }

    // While loop
    int counter = 0;
    while (counter < 5) {
        printf("Counter: %d \\n", counter);
        counter++;
    }

    return 0;
}'''
        
        try:
            with open('example.txt', 'w', encoding='utf-8') as f:
                f.write(sample_content)
            return True
        except Exception:
            return False
    
    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Select code file",
            filetypes=[("Text files", "*.txt"),
                      ("C/C++ files", "*.c *.cpp *.h"),
                      ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.delete('1.0', 'end')
                self.code_editor.insert('1.0', content)
                self.update_line_numbers()
                self.analysis_status.config(text=f"File loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file:\n{e}")
    
    def load_sample(self):
        if os.path.exists('example.txt'):
            try:
                with open('example.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.delete('1.0', 'end')
                self.code_editor.insert('1.0', content)
                self.update_line_numbers()
                self.analysis_status.config(text="Example code loaded")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load example:\n{e}")
        else:
            messagebox.showwarning("Warning", "Example file does not exist")
    
    def clear_editor(self):
        self.code_editor.delete('1.0', 'end')
        self.update_line_numbers()
        self.clear_analysis()
        self.analysis_status.config(text="Editor cleared")
    
    def clear_analysis(self):
        # Clear token table
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        self.total_tokens_label.config(text="Total Tokens: 0")
        
        # Clear classification
        self.classification_text.config(state='normal')
        self.classification_text.delete('1.0', 'end')
        self.classification_text.config(state='disabled')
    
    def analyze_code(self):
        code = self.code_editor.get('1.0', 'end-1c')
        
        if not code.strip():
            messagebox.showwarning("Warning", "No code to analyze")
            return
        
        try:
            # Lexical analysis
            tokens = self.analyzer.tokenize(code)
            
            # Clear previous analysis
            self.clear_analysis()
            
            # Fill token table (excluding comments)
            valid_tokens = [token for token in tokens if token.type not in ['COMMENT_SINGLE', 'COMMENT_MULTI']]
            
            for i, token in enumerate(tokens):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.token_tree.insert('', 'end', 
                                     values=(token.type, token.value, token.line, token.column),
                                     tags=(tag,))
            
            # Update statistics (excluding comments)
            token_count = len(valid_tokens)
            self.total_tokens_label.config(text=f"Total Tokens: {token_count}")
            self.analysis_status.config(text=f"Analysis completed - {token_count} tokens found")
            
            # Generate classification
            self.update_classification(valid_tokens)
            
            # Switch to analysis tab
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during analysis:\n{e}")
    
    def update_classification(self, tokens):
        """Update the classification tab with categorized tokens"""
        classification = self.analyzer.classify_tokens(tokens)
        
        # Build classification text
        classification_text = "TOKEN CLASSIFICATION\n"
        classification_text += "=" * 60 + "\n\n"
        
        # Keywords
        classification_text += f"1. Keywords: {', '.join(set(classification['keywords'])) if classification['keywords'] else '(none)'}\n"
        
        # Identifiers  
        classification_text += f"2. Identifiers: {', '.join(set(classification['identifiers'])) if classification['identifiers'] else '(none)'}\n"
        
        # Punctuations
        classification_text += f"3. Punctuations: {', '.join(set(classification['punctuations'])) if classification['punctuations'] else '(none)'}\n"
        
        # Operators
        classification_text += f"4. Operators: {', '.join(set(classification['operators'])) if classification['operators'] else '(none)'}\n"
        
        # Constants
        classification_text += f"5. Constants: {', '.join(set(classification['constants'])) if classification['constants'] else '(none)'}\n"
        
        # Literals
        classification_text += f"6. Literals: {', '.join(set(classification['literals'])) if classification['literals'] else '(none)'}\n\n"
        
        # Total count (excluding comments)
        total_count = len(tokens)
        classification_text += f"Count = {total_count} tokens\n\n"
        
        # Detailed breakdown
        classification_text += "DETAILED BREAKDOWN:\n"
        classification_text += "-" * 40 + "\n"
        
        categories = [
            ("Keywords", classification['keywords']),
            ("Identifiers", classification['identifiers']),
            ("Punctuations", classification['punctuations']),
            ("Operators", classification['operators']),
            ("Constants", classification['constants']),
            ("Literals", classification['literals'])
        ]
        
        for category, items in categories:
            if items:
                classification_text += f"\n{category} ({len(items)} total):\n"
                # Remove duplicates but maintain order
                seen = set()
                unique_items = []
                for item in items:
                    if item not in seen:
                        seen.add(item)
                        unique_items.append(item)
                
                for item in unique_items:
                    count = items.count(item)
                    classification_text += f"  • {item} (appears {count} time{'s' if count > 1 else ''})\n"
        
        # Update the text widget
        self.classification_text.config(state='normal')
        self.classification_text.delete('1.0', 'end')
        self.classification_text.insert('1.0', classification_text)
        self.classification_text.config(state='disabled')
    
    # def load_grammar(self):
    #     grammar_text = self.cfg.get_grammar_text()
    #     self.grammar_text.config(state='normal')
    #     self.grammar_text.delete('1.0', 'end')
    #     self.grammar_text.insert('1.0', grammar_text)
    #     self.grammar_text.config(state='disabled')

def main():
    root = tk.Tk()
    
    # Set icon (optional)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = LexicalAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
