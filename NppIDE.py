import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class AutoComplete:
    def __init__(self, text, words):
        self.text = text
        self.words = sorted(set(words))

        self.listbox = tk.Listbox(
            text.master,
            height=6,
            bg="#111111",
            fg="white",
            selectbackground="#007acc",
            relief="solid"
        )

        self.visible = False

        self.text.bind(
            "<KeyRelease>",
            lambda e: self.text.after_idle(self.update),
            add="+"
        )
        self.text.bind("<Down>", self.move_down)
        self.text.bind("<Up>", self.move_up)
        self.text.bind("<Return>", self.complete)
        self.text.bind("<Tab>", self.complete)
        self.text.bind("<BackSpace>", lambda e: self.text.after_idle(self.update), add="+")
        self.text.bind("<Delete>", lambda e: self.text.after_idle(self.update), add="+")

    def current_word(self):
        line = self.text.get("insert linestart", "insert")
        m = re.search(r"[A-Za-z_][A-Za-z0-9_]*$", line)
        return m.group(0) if m else ""

    def update(self, event=None):
    
        # Ignore only navigation keys
        if event and event.keysym in (
            "Up", "Down", "Left", "Right",
            "Return", "Tab", "Escape"
        ):
            return
    
        word = self.current_word()
    
        if not word:
            self.hide()
            return
    
        # Recalculate matches every keystroke
        matches = sorted(
            w for w in self.words
            if w.lower().startswith(word.lower()) and w != word
        )
    
        self.listbox.delete(0, tk.END)
    
        if not matches:
            self.hide()
            return
    
        for match in matches[:10]:
            self.listbox.insert(tk.END, match)
    
        bbox = self.text.bbox("insert")
        if bbox is None:
            self.hide()
            return
    
        x, y, w, h = bbox
    
        x += self.text.winfo_x()
        y += self.text.winfo_y()
    
        self.listbox.place(
            x=x,
            y=y + h,
            width=180
        )
    
        self.visible = True
    
        # Always select the first suggestion
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(0)
        self.listbox.activate(0)

    def hide(self):
        self.listbox.place_forget()
        self.visible = False

    def complete(self, event=None):
        if not self.visible:
            return

        word = self.current_word()

        if not word:
            return

        choice = self.listbox.get(tk.ACTIVE)

        self.text.delete(
            f"insert-{len(word)}c",
            "insert"
        )

        self.text.insert("insert", choice)

        self.hide()

        return "break"

    def move_down(self, event):
        if not self.visible:
            return

        cur = self.listbox.curselection()

        if cur:
            i = min(cur[0] + 1, self.listbox.size() - 1)
        else:
            i = 0

        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(i)
        self.listbox.activate(i)

        return "break"

    def move_up(self, event):
        if not self.visible:
            return

        cur = self.listbox.curselection()

        if cur:
            i = max(cur[0] - 1, 0)
        else:
            i = 0

        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(i)
        self.listbox.activate(i)

        return "break"
        
class CustomHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget

        # Your custom language rules
        self.keywords = [
            "while", "for", "public", "private", "func", "class", "load", "rename", "inherit",
            "if", "else", "open", "sync", "desync", "attempt", "catch", "in", "ignore", "break", "continue",
            "import", "get", "and", "is", "as", "not", "or", "global", "return", "True", "False"
        ]

        self.builtins = [
            "output", "quit", "num", "input", "eval", "exec", "length", "sort", "min", "mean", "max", "median", "mode", "sum", "range", "call", "reverse", "type", "format",
            "zip", "dict", "map"
        ]


        self.token_patterns = [
            ("comment", r"//.*|#.*"),
            ("string", r'"[^"\n]*"|\'[^\'\n]*\''),
            ("number", r"\b\d+(\.\d+)?\b"),
            ("keyword", r"\b(" + "|".join(map(re.escape, self.keywords)) + r")\b"),
            ("builtin", r"\b(" + "|".join(map(re.escape, self.builtins)) + r")\b"),
            ("operator", r"[\+\-\*/=<>\!:]+"),
            ("brace", r"[\(\)\[\]\{\}]"),
        ]

        self.configure_tags()

    def configure_tags(self):
        self.text.tag_configure("comment", foreground="#7f8c8d", font=("Fire Code 12", 6, "italic"))
        self.text.tag_configure("string", foreground="#f1c40f")
        self.text.tag_configure("number", foreground="#9b59b6")
        self.text.tag_configure("keyword", foreground="#3498db", font=("Fira Code 12", 6, "bold"))
        self.text.tag_configure("builtin", foreground="#2ecc71")
        self.text.tag_configure("operator", foreground="#e74c3c")
        self.text.tag_configure("brace", foreground="#bdc3c7")

    def highlight(self, event=None):
        text = self.text
        content = text.get("1.0", "end-1c")

        # Remove previous highlighting
        for tag, _ in self.token_patterns:
            text.tag_remove(tag, "1.0", "end")

        # Apply highlighting
        for tag, pattern in self.token_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text.tag_add(tag, start, end)

        return "break"


class EditorTab:
    def __init__(self, parent, theme):
        self.frame = ttk.Frame(parent)
        self.filepath = None
        self.container = ttk.Frame(self.frame)
        self.container.pack(fill="both", expand=True)

        self.line_numbers = tk.Text(
            self.container,
            width=3,
            padx=5,
            takefocus=0,
            border=1,
            state="disabled",
            wrap="none",
            bg=theme["linen_bg"],
            fg=theme["linen_fg"],
            insertbackground=theme["text_fg"],
            font=("Sans", 6),
        )
        self.line_numbers.pack(side="left", fill="y")

        self.text = tk.Text(
            self.container,
            undo=True,
            wrap="none",
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["cursor"],
            selectbackground=theme["selection"],
            selectforeground=theme["selection_fg"],
            relief="flat",
            border=0,
            font=("Sans", 6),
            padx=11,
            pady=11,
        )
        self.text.pack(side="left", fill="both", expand=True)

        self.scrollbar_y = ttk.Scrollbar(self.container, orient="vertical", command=self._on_scroll_y)
        self.scrollbar_y.pack(side="right", fill="y")

        self.scrollbar_x = ttk.Scrollbar(self.frame, orient="horizontal", command=self.text.xview)
        self.scrollbar_x.pack(side="bottom", fill="x")

        self.text.configure(yscrollcommand=self._sync_scroll_y, xscrollcommand=self.scrollbar_x.set)

        self.highlighter = CustomHighlighter(self.text)
        words = (
            self.highlighter.keywords +
            self.highlighter.builtins
        )
        
        self.autocomplete = AutoComplete(
            self.text,
            words
        )

        self.text.bind("<KeyRelease>", self.on_change, add="+")
        self.text.bind("<MouseWheel>", self.on_change)
        self.text.bind("<ButtonRelease-1>", self.on_change)
        self.text.bind("<Return>", self.on_return)
        self.text.bind("<Tab>", self.on_tab)
        self.text.bind("<Control-s>", self.on_save_shortcut)
        self.text.bind("(", self.open_paren)
        self.text.bind("[", self.open_bracket)
        self.text.bind("{", self.open_brace)
        self.text.bind('"', self.open_double_quote)
        self.text.bind("'", self.open_single_quote)

        self._update_line_numbers()
    
    def _insert_pair(self, left, right):
        self.text.insert("insert", left + right)
        self.text.mark_set("insert", "insert-1c")
        self.on_change()
        return "break"
    
    def open_paren(self, event):
        return self._insert_pair("(", ")")
    
    def open_bracket(self, event):
        return self._insert_pair("[", "]")
    
    def open_brace(self, event):
        return self._insert_pair("{", "}")
    
    def open_double_quote(self, event):
        return self._insert_pair('"', '"')
    
    def open_single_quote(self, event):
        return self._insert_pair("'", "'")
        
    def on_tab(self, event):

        if self.autocomplete.visible:
            return self.autocomplete.complete(event)
    
        self.text.insert("insert", "    ")
        self.on_change()
        return "break"

    def on_save_shortcut(self, event):
        return "break"

    def on_change(self, event=None):
        self.highlighter.highlight()
        self._update_line_numbers()
    
    def on_return(self, event):

        if self.autocomplete.visible:
            return self.autocomplete.complete(event)
        text = self.text
    
        current_line = text.get("insert linestart", "insert")
    
        indent = ""
    
        for ch in current_line:
            if ch in " \t":
                indent += ch
            else:
                break
    
        text.insert("insert", "\n" + indent)
    
        self.on_change()
    
        return "break"
        
    def _update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")

        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state="disabled")
    
    
    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("JSON Files", "*.json"),
                ("Markdown", "*.md"),
                ("All Files", "*.*"),
                ("Npp Files", "*.npp")
            ]
        )
    
        if not path:
            return
    
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
    
        tab = self.current_tab()
    
        tab.text.delete("1.0", "end")
        tab.text.insert("1.0", content)
        tab.on_change()
    
        self.notebook.tab(
            self.notebook.select(),
            text=os.path.basename(path)
        )
    
        tab.filepath = path
    def save_file(self):
        tab = self.current_tab()
    
        if tab.filepath is None:
            return self.save_as()
    
        with open(tab.filepath, "w", encoding="utf-8") as f:
            f.write(tab.text.get("1.0", "end-1c"))
    
    def save_as(self):
        tab = self.current_tab()
    
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*")]
        )
    
        if not path:
            return
    
        with open(path, "w", encoding="utf-8") as f:
            f.write(tab.text.get("1.0", "end-1c"))
    
        tab.filepath = path
    
        self.notebook.tab(
            self.notebook.select(),
            text=os.path.basename(path)
        )
        
    def _on_scroll_y(self, *args):
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def _sync_scroll_y(self, first, last):
        self.scrollbar_y.set(first, last)
        self.line_numbers.yview_moveto(first)

    def get_text(self):
        return self.text.get("1.0", "end-1c")

    def set_text(self, value):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.on_change()


class NotebookIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Notebook IDE")
        self.root.geometry("1100x700")

        self.theme = {
            "bg": "#151515",
            "text_bg": "#111111",
            "text_fg": "#d1d1d1",
            "linen_bg": "#1A1A1A",
            "linen_fg": "#c1c1c1",
            "cursor": "#ffffff",
            "selection": "#264f78",
            "selection_fg": "#ffffff",
        }

        self.root.configure(bg=self.theme["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.theme["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background="#333333", foreground="white", padding=(14, 8))
        style.map("TNotebook.Tab", background=[("selected", "#333333")])

        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x")
        
        bottom_bar = ttk.Frame(root)
        bottom_bar.pack(side="bottom", fill="x")
        
        symbols = [
            "Tab",
            ";", ".", ",",
            "(", ")", "[", "]", "{", "}",
            "=", "+", "-", "*", "/",
            ":", "\"", "'"
        ]
        
        for symbol in symbols:
        
            def insert_symbol(s=symbol):
                tab = self.current_tab()
                if not tab:
                    return
        
                if s == "Tab":
                    tab.text.insert("insert", "    ")
                else:
                    tab.text.insert("insert", s)
        
                tab.on_change()
        
            ttk.Button(
                bottom_bar,
                text=symbol,
                width=3,
                command=insert_symbol
            ).pack(side="left", padx=1, pady=2)

        ttk.Button(toolbar, text="New Tab", command=self.new_tab).pack(side="left", padx=3, pady=3)
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side="left", padx=3, pady=3)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side="left", padx=3, pady=3)
        ttk.Button(toolbar, text="Highlight All", command=self.highlight_active).pack(side="left", padx=3, pady=3)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = []
        self.new_tab()

    def current_tab(self):
        current = self.notebook.nametowidget(self.notebook.select())
        for tab in self.tabs:
            if tab.frame == current:
                return tab
        return None
    
        
    def new_tab(self):
        tab = EditorTab(self.notebook, self.theme)
        self.tabs.append(tab)
        self.notebook.add(tab.frame, text=f"File {len(self.tabs)}")
        self.notebook.select(tab.frame)

        sample = """"""
        tab.set_text(sample)

    def highlight_active(self):
        tab = self.current_tab()
        if tab:
            tab.on_change()

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*"), ("Npp files", "*.npp")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror("Open failed", str(e))
            return

        tab = self.current_tab()
        if tab is None:
            self.new_tab()
            tab = self.current_tab()

        tab.set_text(data)
        self.notebook.tab(self.notebook.select(), text=path.split("/")[-1])

    def save_file(self):
        tab = self.current_tab()
        if tab is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*"), ("Npp files", "*.npp")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(tab.get_text())
            self.notebook.tab(self.notebook.select(), text=path.split("/")[-1])
        except Exception as e:
            messagebox.showerror("Save failed", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = NotebookIDE(root)
    root.mainloop()