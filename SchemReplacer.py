import os
import nbtlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, relief=tk.SOLID, borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def load_schem_files(schem_files):
    schem_data_dict = {}

    for schem_file in schem_files:
        schem_data = nbtlib.File.load(schem_file, gzipped=True)
        schem_data_dict[schem_file] = schem_data

    return schem_data_dict

def replace_blocks(schem_data, block_to_replace, replace_with):
    replaced_blocks = 0
    if not schem_data:
        return "Invalid schematic data"

    if 'Palette' in schem_data:
        palette = schem_data['Palette']

        if "[" not in block_to_replace and "[" in replace_with and any(replace_with.split("[")[0]+"[" in item for item in palette):
            return "Please remove the properties of the replacement block (everything in brackets) to prevent conflicts."

        if block_to_replace == replace_with:
            return "The 'block_to_replace' and 'replace_with' are identical. No need to replace blocks."

        found = False

        for block in palette:
            if "[" not in block_to_replace:
                if block_to_replace == block.split("[")[0]:
                    found = True
                    break
            else:
                if block_to_replace == block:
                    found = True
                    break

        if found == False:
            return f"No matching blocks found for: {block_to_replace}"

        changes = []

        if "[" in block_to_replace:
            for block in palette:
                if block == block_to_replace:
                    changes.append((block, replace_with))
        else:
            for block in palette:
                if block_to_replace == block.split("[")[0]:
                    new_key = block.replace(block_to_replace, replace_with)
                    changes.append((block, new_key))

        for old_key, new_key in changes:
            to_replace_index = palette[old_key]
            if new_key in palette:
                replace_with_index = palette[new_key]
                block_data = schem_data['BlockData']

                block_data_bytes = bytearray(block_data)

                for i, block in enumerate(block_data_bytes):
                    if block == to_replace_index:
                        block_data_bytes[i] = replace_with_index

                schem_data['BlockData'] = nbtlib.ByteArray(block_data_bytes)
            else:
                palette[new_key] = palette.pop(old_key)

            # Remove the original block from palette after replacing, then re-index both the Palette and Blockdata to prevent errors when file is read
            if old_key in palette:
                old_index = palette[old_key]
                del palette[old_key]

                # Decrement the indices of all blocks in the palette that come after the removed block.
                for block, index in palette.items():
                    if index > old_index:
                        palette[block] = nbtlib.Int(index - 1)

                # Decrement the indices in the 'BlockData' ByteArray that correspond to these blocks.
                block_data = schem_data['BlockData']
                block_data_bytes = bytearray(block_data)
                for i, block in enumerate(block_data_bytes):
                    if block > old_index:
                        block_data_bytes[i] = block - 1
                schem_data['BlockData'] = nbtlib.ByteArray(block_data_bytes)

        replaced_blocks += 1

        schem_data['PaletteMax'] = nbtlib.Int(len(palette))

        return f"Replaced {replaced_blocks} blocks"

def save_schem_file(schem_data, filepath):
    try:
        schem_data.save(filepath)
    except Exception as e:
        return f"Error saving file: {e}"

def get_unique_blocks_from_modified_data(modified_schem_data):
    unique_blocks = set()

    for schem_data in modified_schem_data.values():
        palette = schem_data.get('Palette', {})

        for block in palette:
            unique_blocks.add(block)

    return unique_blocks

unsaved_changes = False

def main():
    def show_message(title, message, buttons=False):
        def close_dialog(result=None):
            top.result = result
            top.destroy()

        top = tk.Toplevel()
        top.title(title)

        text = tk.Text(top, wrap=tk.NONE, state=tk.DISABLED)
        text.configure(state=tk.NORMAL)
        text.insert(tk.END, message)
        text.configure(state=tk.DISABLED)

        lines = int(text.index(tk.END).split('.')[0])
        text.configure(height=min(lines, 25))

        max_line_length = max(len(line) for line in message.splitlines()) + 5
        text.configure(width=min(max_line_length, 125))

        scroll = tk.Scrollbar(top, command=text.yview)
        text.configure(yscrollcommand=scroll.set)

        text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)

        top.grid_rowconfigure(0, weight=1)
        top.grid_columnconfigure(0, weight=1)

        button_frame = tk.Frame(top)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='e')

        if buttons:
            yes_button = tk.Button(button_frame, text="Yes", command=lambda: close_dialog(True), width=10)
            yes_button.pack(side=tk.LEFT, padx=(0, 10))

            no_button = tk.Button(button_frame, text="No", command=lambda: close_dialog(False), width=10)
            no_button.pack(side=tk.LEFT)
        else:
            ok_button = tk.Button(button_frame, text="OK", command=lambda: close_dialog(True), width=10)
            ok_button.pack()

        top.wait_window()
        return top.result

    def set_input_widgets_state(state):
        entry_replace_block.config(state=state)
        entry_replace_with.config(state=state)
        button_replace_blocks.config(state=state)
        button_save_changes.config(state=state)
        button_save_copy.config(state=state)

    def on_replace_blocks():
        global unsaved_changes

        nonlocal modified_schem_data
        block_to_replace = entry_replace_block.get()
        replace_with = entry_replace_with.get()

        if block_to_replace == "" or replace_with == "":
            messagebox.showerror("Replace Blocks", "Please fill out all fields.")
        else:
            messages = []
            for filepath in new_schem_files:
                schem_data = modified_schem_data.get(filepath)
                message = replace_blocks(schem_data, block_to_replace, replace_with)
                modified_schem_data[filepath] = schem_data
                messages.append(f"{os.path.basename(filepath)}: {message}")

            unsaved_changes = True
            root.title(".Schem Block Replacer (Unsaved Changes)")

            update_master_list(modified_schem_data)

            show_message("Blocks Replaced", "\n".join(messages), False)

    def on_listbox_select(event):
        selected_block = listbox_master_list.get(listbox_master_list.curselection())
        if last_selected_entry is None:
            entry_replace_block.delete(0, tk.END)
            entry_replace_block.insert(0, selected_block)
        else:
            last_selected_entry.delete(0, tk.END)
            last_selected_entry.insert(0, selected_block)

    def on_entry_click(event):
        nonlocal last_selected_entry
        last_selected_entry = event.widget

    def on_open_files():
        global unsaved_changes
        nonlocal modified_schem_data, new_schem_files
        if unsaved_changes:
            if not messagebox.askyesno("Exit", "There are unsaved changes. Are you sure you want to load new .schem file(s)?"):
                return

        new_schem_files = filedialog.askopenfilenames(title="Select .schem file(s)",
                                                      filetypes=[("Schem Files", "*.schem")])
        if new_schem_files:
            modified_schem_data = load_schem_files(new_schem_files)
            update_master_list(modified_schem_data)
            set_input_widgets_state(tk.NORMAL)
            unsaved_changes = False
            root.title(".Schem Block Replacer")

    def update_master_list(modified_schem_data):
        nonlocal unique_blocks
        unique_blocks = sorted(list(get_unique_blocks_from_modified_data(modified_schem_data)), key=lambda x: x.split(':', 1)[1])
        sort_master_list()

    def sort_master_list():
        sort_by_mod = combo_sort_by_mod.get()

        if sort_by_mod:
            reverse = sort_by_mod == "Z-A"
            unique_blocks.sort(key=lambda x: x.split(':', 1)[0], reverse=reverse)

        listbox_master_list.delete(0, tk.END)
        for block in unique_blocks:
            listbox_master_list.insert(tk.END, block)

    def on_search_blocks():
        search_term = entry_search_block.get().strip().lower()
        listbox_search_results.delete(0, tk.END)
        found_count = 0
        for idx, block in enumerate(unique_blocks):
            if search_term in block.lower():
                listbox_search_results.insert(tk.END, block)
                found_count += 1
        label_found_count.config(text=f"Найдено: {found_count}")

    def on_select_search_result(event):
        selected_block = listbox_search_results.get(listbox_search_results.curselection())
        listbox_master_list.selection_clear(0, tk.END)
        for idx, block in enumerate(unique_blocks):
            if block == selected_block:
                listbox_master_list.selection_set(idx)
                listbox_master_list.see(idx)
                break

    def on_save_changes():
        for filepath, schem_data in modified_schem_data.items():
            save_schem_file(schem_data, filepath)

        global unsaved_changes
        unsaved_changes = False
        root.title(".Schem Block Replacer")
        messagebox.showinfo("Save Changes", "Changes saved successfully!")

    def on_save_copy():
        directory = filedialog.askdirectory(title="Select Directory to Save Copy")
        if not directory:
            return

        for filepath, schem_data in modified_schem_data.items():
            filename = os.path.basename(filepath)
            save_path = os.path.join(directory, filename)
            save_schem_file(schem_data, save_path)

        messagebox.showinfo("Save Copy", "Copies saved successfully!")

    def on_delete_selected():
        selected_idx = listbox_master_list.curselection()
        if not selected_idx:
            messagebox.showwarning("Delete Block", "Please select a block to delete.")
            return
        selected_block = listbox_master_list.get(selected_idx)
        unique_blocks.remove(selected_block)
        listbox_master_list.delete(selected_idx)
        for filepath, schem_data in modified_schem_data.items():
            palette = schem_data.get('Palette', {})
            if selected_block in palette:
                del palette[selected_block]
                schem_data['Palette'] = palette

        update_master_list(modified_schem_data)
        global unsaved_changes
        unsaved_changes = True
        root.title(".Schem Block Replacer (Unsaved Changes)")

    root = tk.Tk()
    root.title(".Schem Block Replacer")
    root.geometry("1000x600")

    frame_top = tk.Frame(root)
    frame_top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    button_open_files = tk.Button(frame_top, text="Open .schem Files", command=on_open_files)
    button_open_files.pack(side=tk.LEFT)

    button_save_changes = tk.Button(frame_top, text="Save Changes", command=on_save_changes, state=tk.DISABLED)
    button_save_changes.pack(side=tk.LEFT, padx=5)

    button_save_copy = tk.Button(frame_top, text="Save Copy", command=on_save_copy, state=tk.DISABLED)
    button_save_copy.pack(side=tk.LEFT, padx=5)

    frame_replace = tk.Frame(root)
    frame_replace.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    label_replace_block = tk.Label(frame_replace, text="Block to Replace:")
    label_replace_block.pack(side=tk.LEFT)

    entry_replace_block = tk.Entry(frame_replace, width=30, state=tk.DISABLED)
    entry_replace_block.pack(side=tk.LEFT, padx=5)
    entry_replace_block.bind("<FocusIn>", on_entry_click)

    label_replace_with = tk.Label(frame_replace, text="Replace With:")
    label_replace_with.pack(side=tk.LEFT)

    entry_replace_with = tk.Entry(frame_replace, width=30, state=tk.DISABLED)
    entry_replace_with.pack(side=tk.LEFT, padx=5)
    entry_replace_with.bind("<FocusIn>", on_entry_click)

    button_replace_blocks = tk.Button(frame_replace, text="Replace Blocks", command=on_replace_blocks, state=tk.DISABLED)
    button_replace_blocks.pack(side=tk.LEFT, padx=5)

    frame_search = tk.Frame(root)
    frame_search.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    label_search_block = tk.Label(frame_search, text="Search Block:")
    label_search_block.pack(side=tk.LEFT)

    entry_search_block = tk.Entry(frame_search, width=30)
    entry_search_block.pack(side=tk.LEFT, padx=5)

    button_search_blocks = tk.Button(frame_search, text="Search", command=on_search_blocks)
    button_search_blocks.pack(side=tk.LEFT, padx=5)

    label_found_count = tk.Label(frame_search, text="Найдено: 0")
    label_found_count.pack(side=tk.LEFT, padx=5)

    frame_sort = tk.Frame(root)
    frame_sort.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    label_sort_by_mod = tk.Label(frame_sort, text="Sort by Mod:")
    label_sort_by_mod.pack(side=tk.LEFT)

    combo_sort_by_mod = ttk.Combobox(frame_sort, values=["", "A-Z", "Z-A"])
    combo_sort_by_mod.pack(side=tk.LEFT, padx=5)
    combo_sort_by_mod.bind("<<ComboboxSelected>>", lambda e: sort_master_list())

    frame_lists = tk.Frame(root)
    frame_lists.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    frame_master_list = tk.Frame(frame_lists)
    frame_master_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    label_master_list = tk.Label(frame_master_list, text="Master List")
    label_master_list.pack(side=tk.TOP)

    listbox_master_list = tk.Listbox(frame_master_list, selectmode=tk.SINGLE)
    listbox_master_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_master_list = tk.Scrollbar(frame_master_list)
    scrollbar_master_list.pack(side=tk.RIGHT, fill=tk.Y)
    listbox_master_list.config(yscrollcommand=scrollbar_master_list.set)
    scrollbar_master_list.config(command=listbox_master_list.yview)

    listbox_master_list.bind('<<ListboxSelect>>', on_listbox_select)

    frame_search_results = tk.Frame(frame_lists)
    frame_search_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    label_search_results = tk.Label(frame_search_results, text="Search Results")
    label_search_results.pack(side=tk.TOP)

    listbox_search_results = tk.Listbox(frame_search_results, selectmode=tk.SINGLE)
    listbox_search_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_search_results = tk.Scrollbar(frame_search_results)
    scrollbar_search_results.pack(side=tk.RIGHT, fill=tk.Y)
    listbox_search_results.config(yscrollcommand=scrollbar_search_results.set)
    scrollbar_search_results.config(command=listbox_search_results.yview)

    listbox_search_results.bind('<<ListboxSelect>>', on_select_search_result)

    button_delete_selected = tk.Button(root, text="Удалить выбранный блок", command=on_delete_selected)
    button_delete_selected.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    last_selected_entry = None
    new_schem_files = []
    modified_schem_data = {}
    unique_blocks = []

    root.mainloop()

if __name__ == "__main__":
    main()
