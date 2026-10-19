#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26  2024

@author: Tommaso Fogarin, email: fogarintommaso@gmail.com
"""


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import os
import h5py
import numpy as np
from PIL import ImageGrab



def graphs_analyser(mainwindow):
 """
 This program is used to analyze graphs obtained from RIXS methods, 
 with the data saved in HDF5 files
 """
 
    
 global root, selected_lines, peak_value, low_value
 
 low_value=0
 peak_value=0
 
 # Funzione per gestire il salvataggio
 def save_action():
    # Specifica il percorso e il nome del file dove salvare l'immagine
    save_path = "saved_window_image.png"  # Puoi cambiare il percorso e il nome del file qui
    
    # Ottieni la posizione della finestra Tkinter
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    width = root.winfo_width()
    height = root.winfo_height()
    
    # Cattura l'immagine della finestra
    ImageGrab.grab((x, y, x + width, y + height)).save(save_path)

    messagebox.showinfo("Save", f"Window saved as {save_path}.")

 # Funzione per gestire il refresh
 def refresh_action():
    # Chiudi la finestra corrente
    root.quit()  # Chiude l'applicazione Tkinter
    root.destroy()  # Distrugge la finestra corrente
    graphs_analyser(mainwindow)

 # Funzione per gestire l'uscita
 def quit_action():
    root.quit()
    root.destroy()

 # Funzione per la sezione "About"
 def about_action():
    # Create a Toplevel window
    presentation_window = tk.Toplevel(root)
    presentation_window.title("Project Presentation")

    # Set the size of the window
    presentation_window.geometry("600x300+200+200")
    
    # Create a frame for better organization
    frame = tk.Frame(presentation_window, padx=10, pady=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Create a title label
    title_label = tk.Label(frame, text="Project Presentation", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)

    # Create a text widget for the presentation content
    presentation_text = (
        "This graphical interface was developed by Tommaso Fogarin during his internship "
        "at the Soleil Synchrotron while studying for his Engineering Physics degree at Ca' Foscari University. "
        "The project was commissioned by Alessandro Nicolau, with supervision provided by both him and Victor Porée, "
        "with the primary goal of simplifying the work of researchers and guests at the Sextant beamline.\n\n"
        "For any questions or potential collaborations, please do not hesitate to contact me at:\n"
        "Email: fogarintommaso@gmail.com\n\n"
        "Paris, 07/10/2024\n\n"
    )

    text_widget = tk.Text(frame, wrap=tk.WORD, font=("Helvetica", 14), bg="lightyellow", padx=10, pady=10)
    text_widget.insert(tk.END, presentation_text)
    text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
    text_widget.pack(expand=True, fill=tk.BOTH)
    
 
 # Definisci le variabili globali all'esterno della classe

 class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window, data, title):
        super().__init__(canvas, window)
        self.data = data  # Salva i dati come variabile di istanza
        self.title = title  # Salva il titolo come variabile di istanza
        self.window = window

        # Aggiungi gli Entry widget per la selezione dei valori
        self.add_entry_widgets()
        
        # Aggiungi il pulsante di reset
        self.add_reset_button()

    def add_entry_widgets(self):
        # Label per l'input del "Peaks cut"
        self.label_peaks = tk.Label(self, text="Upperbound:")
        self.label_peaks.pack(side=tk.LEFT, padx=2, pady=2)

        # Entry widget per inserire il valore di "Peaks cut"
        self.entry_peaks = tk.Entry(self, width=5)
        self.entry_peaks.pack(side=tk.LEFT, padx=2, pady=2)
        self.entry_peaks.insert(0, str(np.max(self.data))) # Inserisci l'ultimo valore globale
        self.entry_peaks.bind('<Return>', self.apply_peaks_cut)  # Associa l'evento Enter

        # Label per l'input del "Low cut"
        self.label_low = tk.Label(self, text="Lowerbound:")
        self.label_low.pack(side=tk.LEFT, padx=2, pady=2)

        # Entry widget per inserire il valore di "Low cut"
        self.entry_low = tk.Entry(self, width=5)
        self.entry_low.pack(side=tk.LEFT, padx=2, pady=2)
        self.entry_low.insert(0,str(np.min(self.data)))  # Inserisci l'ultimo valore globale
        self.entry_low.bind('<Return>', self.apply_low_cut)  # Associa l'evento Enter
    def add_reset_button(self):
        # Aggiungi il pulsante "Reset" alla toolbar
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_values)
        self.reset_button.pack(side=tk.LEFT, padx=2, pady=2)
    def reset_values(self):
        
        global low_value, peak_value
        # Ripristina i dati originali e i valori di upperbound e lowerbound
        dat,name= get_data_name()
        peak_value=np.max(dat)
        self.entry_peaks.delete(0, tk.END)
        self.entry_peaks.insert(0, str(peak_value))  # Ripristina il massimo originale
        
        low_value = np.min(dat)
        self.entry_low.delete(0, tk.END)
        self.entry_low.insert(0, str(low_value))  # Ripristina il minimo originale

        # Ridisegna la heatmap con i dati originali
        plot_image(self.window, dat, name)
        
    def apply_peaks_cut(self, event=None):
        global peak_value  # Dichiara che userai la variabile globale
        try:
            peak_value = float(self.entry_peaks.get())  # Aggiorna la variabile globale
            # Modifica i dati per normalizzarli
            normalized_data = np.clip(self.data, None, peak_value)  # Imposta i valori sopra 'high_bound' a 'high_bound'
            # Ridisegna la heatmap con i dati normalizzati
            plot_image(self.window, normalized_data, self.title)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter a valid number for Peaks cut")

    def apply_low_cut(self, event=None):
        global low_value  # Dichiara che userai la variabile globale
        try:
            low_value = float(self.entry_low.get())  # Aggiorna la variabile globale
            # Modifica i dati per normalizzarli
            normalized_data = np.clip(self.data, low_value, None)  # Imposta i valori sotto 'low_bound' a 'low_bound'
            # Ridisegna la heatmap con i dati normalizzati
            plot_image(self.window, normalized_data, self.title)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter a valid number for Low cut")

 # Main window
 # First column

 def folder(event=None):
     """
     It takes the folder path from the entry widget and populates the listbox with .hdf5 files
     sorted by creation date from the most recent to the oldest.
     """
     folder_path = entrypath.get()
     if not os.path.isdir(folder_path):
         messagebox.showerror("Error", f"The path '{folder_path}' is not a valid directory.")
         return
     
     # Lista di tuple (file, data_di_creazione)
     files_with_dates = [
         (f, os.path.getctime(os.path.join(folder_path, f)))
         for f in os.listdir(folder_path)
         if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".hdf5")
     ]
     
     # Ordina la lista in base alla data di creazione (il secondo elemento della tupla)
     files_with_dates.sort(key=lambda x: x[1], reverse=True)
     
     # Pulisce la Listbox e inserisce i file ordinati
     listbox.delete(0, tk.END)
     for file, _ in files_with_dates:
         listbox.insert(tk.END, file)
         

 def on_listbox_select(event=None):
     """
     Handles the selection of a file in the listbox and sends the file 
     path to the handle_file() function.
     """
     selected_index = listbox.curselection()
     if selected_index:
         file_name = listbox.get(selected_index[0])
         folder_path = entrypath.get()
         file_path = os.path.join(folder_path, file_name)
         handle_file(file_path)
         
 def get_data_name():
     
     if c2_entry_var.get() == "enter" or c2_entry_var.get() == "" :
       if c2_bool1.get():
         
         data,name=spectra_curve_correctedNAccImage,"SpectraCorrectedNAccImage"
       else:
         data,name=spectra_image,"SpectraImage"
         
     else:
         data,name=c2_binning(1)
     return data,name

 def plot_image(frame, data, title):
    """
    Plots a heatmap as an image in the specified frame with the provided data.
    Applies peak_value and low_value cuts if they are set (i.e., different from 0).
    """

    # Controlla se peak_value o low_value sono diversi da zero
    if peak_value != np.max(data)  or low_value != np.min(data):
        # Applica i tagli ai dati basati su peak_value e low_value
        data = np.clip(data, low_value if low_value != np.min(data) else None, peak_value if peak_value != np.max(data)  else None)

    # Rimuovi i widget esistenti nel frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Crea la figura e la heatmap
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    cax = ax.imshow(data, aspect='auto')
    ax.set_title(title)
    
    # Aggiungi una barra dei colori
    cbar = fig.colorbar(cax, ax=ax, fraction=0.030, pad=0.02)
    cbar.ax.tick_params(labelsize=7)

    # Aggiungi eventuali linee selezionate
    if selected_lines:
        for line_index in selected_lines:
            ax.axhline(y=line_index, color='red', linewidth=1.5, linestyle='--')

    # Inserisci il grafico nel widget Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Aggiungi la toolbar personalizzata
    toolbar = CustomToolbar(canvas, frame, data, title)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Configura l'event handler per il right-click, se necessario
    if frame != frame_grafico1:
        canvas.mpl_connect('button_press_event', lambda event: on_right_click2(event, data, title, frame_grafico_right2, y2shift2))

    plt.close(fig) 
     
     
 def handle_file(path):
     """
     Opens the selected .hdf5 file and saves the datasets as global variables. 
     Then, it initializes the main window.
     """
     global spectra_image, curve_corrected_arc, spectra_curve_correctedNAccImage
     global spectra_corrected_NAccImage, corrected_acc, base_acc, low_value, peak_value
     
     with h5py.File(path, 'r') as file:
         spectra_image = file['spectraImage'][:]
         curve_corrected_arc = file['curveCorrectedAcc'][:]
         spectra_curve_correctedNAccImage = file["spectraCurveCorrectedNAccImage"][:]
         spectra_corrected_NAccImage = file["spectraCorrectedNAccImage"][:]
         corrected_acc = file["correctedAcc"][:]
         base_acc = file["baseAcc"][:]
         
     #initialization
     c3_bool1.set(False)
     c3_bool2.set(False)
     c3_bool3.set(False)
     c3_check1.select()
     c2_entry_var.set("enter")
     c2_bool1.set(False)
     
     if low_value==0 and peak_value==0:
       low_value = np.min(spectra_image)
       peak_value = np.max(spectra_image)
     
     plot_image(frame_grafico1, spectra_image, "SpectraImage")
     plot_selected_graphs()


 # Second column

 def c2_correction(frame):
     """
     Handles the spectra visualization adjustment based on the checkbox selection.
     """
     for widget in frame.winfo_children():
         widget.destroy()
     if c2_entry_var.get() == "enter" or c2_entry_var.get() == "" :
       if c2_bool1.get():
         plot_image(frame, spectra_curve_correctedNAccImage, "spectraCurveCorrectedNAccImage")
       else:
         plot_image(frame, spectra_image, "SpectraImage")
     else:
         c2_binning(frame)
         

 def c2_binning(frame, event = None):
     """
     Performs row binning of the matrix.
     If frame=1, it returns the binned data; otherwise, it plots the data.
     """
     
     try:
         N = int(c2_entry_var.get())

         if N <= 0:
             raise ValueError("The parameter N must be a positive integer.")
         if c2_bool1.get():
           matrix = spectra_curve_correctedNAccImage  
           nome= "spectraCurveCorrectedNAccImage"
         else:
             matrix=spectra_image
             nome="SpectraImage"
             
         num_rows = matrix.shape[0]

         if N > num_rows:
             raise ValueError(f"The parameter N cannot exceed the number of rows in the matrix. Matrix rows: {num_rows}, Provided value: {N}")

         num_groups = (num_rows + N - 1) // N
         binned_matrix =np.array([np.mean(matrix[i*N:min((i+1)*N, num_rows)], axis=0) for i in range(num_groups)])
         
         # if input = 1 get the data else plot the image
         if frame==1:
           return binned_matrix,f"Binned {nome} by {N}"
           
         else:
           plot_image(frame, binned_matrix, f"Binned {nome} by {N}")
           

     except ValueError as e:
         messagebox.showerror("Error", str(e))
     except Exception as e:
         messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
   
     
 # Third column

 def plot_selected_graphs():
     """
     Plots the graphs based on the checkboxes selected in column 3.
     """
     data_array = np.array([
         [c3_bool1.get(), curve_corrected_arc],
         [c3_bool2.get(), base_acc],
         [c3_bool3.get(), corrected_acc]
     ], dtype=object)

     names = [("curveCorrectedAcc", "black"), ("baseAcc", "green"), ("correctedAcc", "red")]

     for widget in frame_grafico2.winfo_children():
         widget.destroy()

     fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

     for i in range(3):
         if data_array[i, 0]:
             ax.plot(data_array[i, 1], color=names[i][1], label=f'{names[i][0]}', markersize=3/5-i/3, alpha=0.7+i/8)

     if any(data_array[:, 0]):
         ax.legend(loc='upper right')

     canvas = FigureCanvasTkAgg(fig, master=frame_grafico2)
     canvas.draw()
     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

     toolbar = NavigationToolbar2Tk(canvas, frame_grafico2)
     toolbar.update()
     canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

     plt.close(fig)
     

 #Second window: heatmap analyser:

 def window_heatmap():
     """
     Open a new window for the analysis of the heatmap.
     """
     global new_window
     new_window = tk.Toplevel(root)
     new_window.title("Heatmap Analyser")
     new_window.geometry("1600x800+200+200")
     heatmap_window_layout(new_window)
     new_window.protocol("WM_DELETE_WINDOW", lambda: (selected_lines.clear(),new_window.destroy()))
 def combined_callback1(frame_heatmap, frame_grafico1,entry_sampling_interval, entry_y_shift, frame_grafico_right, event=None):
     """
     Combined function to handle the Return event on entry. 
     Performs binning on both windows.
     """
     c2_binning(frame_grafico1, event)
     c2_binning(frame_heatmap, event)
     stacks_lines(entry_sampling_interval, entry_y_shift, frame_grafico_right)
 def combined_callback2(frame_heatmap, frame_grafico1,entry_sampling_interval, entry_y_shift, frame_grafico_right):
     """
     Combined function to handle the Return event on entry. 
     Performs corrections on both windows.
     """
     c2_correction(frame_grafico1)
     c2_correction(frame_heatmap)
     stacks_lines(entry_sampling_interval, entry_y_shift, frame_grafico_right)
    

 def heatmap_window_layout(window):
     

     global root, frame_grafico_right2, y2shift2, frame_heatmap, entry_sampling_interval, entry_y_shift
     
     # Creazione della menubar
     menubar = tk.Menu(window)

     # Creazione del menu "File"
     file_menu = tk.Menu(menubar, tearoff=0)
     file_menu.add_command(label="Save", command=save_action)
     file_menu.add_command(label="Refresh", command=refresh_action)
     file_menu.add_separator()
     file_menu.add_command(label="Quit", command=quit_action)
     menubar.add_cascade(label="File", menu=file_menu)

     # Creazione del menu "Help"
     help_menu = tk.Menu(menubar, tearoff=0)
     help_menu.add_command(label="About...", command=about_action)
     menubar.add_cascade(label="Help", menu=help_menu)

     # Configura la menubar
     window.config(menu=menubar)
     
     #Two columns layout
     colonna_sinistra = tk.Frame(window)
     colonna_sinistra.grid(row=0, column=0, sticky='nsew', padx=10,pady=10)

     colonna_destra = tk.Frame(window)
     colonna_destra.grid(row=0, column=1, sticky='nsew')
     
     # Configura le righe e colonne per il ridimensionamento
     window.grid_rowconfigure(0, weight=1)
     window.grid_columnconfigure(0, weight=1)
     window.grid_columnconfigure(1, weight=1)

     # Frame per il grafico della heatmap nella colonna sinistra
     frame_heatmap = tk.Frame(colonna_sinistra)
     frame_heatmap.grid(row=1, column=0, sticky='nsew', padx=10,pady=10)

     # Frame per i controlli nella colonna sinistra
     frame_controls_left = tk.Frame(colonna_sinistra)
     frame_controls_left.grid(row=0, column=0, sticky='ew', padx=10)
     
     # Frame aggiuntivo per i bottoni sotto il grafico della heatmap nella colonna sinistra
     frame_lower_buttons_left = tk.Frame(colonna_sinistra)
     frame_lower_buttons_left.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
     
     
     # Bottoni e checkbox nella colonna sinistra
     
     #binning
     label_frameleft = tk.LabelFrame(frame_controls_left, text="Binning sets of n. lines: ",bd=0, relief=tk.FLAT)
     label_frameleft.grid(row=0, column=0, padx=10)
     left_entry_bin = ttk.Entry(label_frameleft, textvariable=c2_entry_var)
     left_entry_bin.grid(row=0, column=0,pady=1)
     left_entry_bin.bind('<Return>',  lambda event: combined_callback1(frame_heatmap, frame_grafico1,entry_sampling_interval, entry_y_shift, frame_grafico_right, event))
     
     #correction
     left_check1 = tk.Checkbutton(frame_controls_left, text="correctedNAccImage", variable=c2_bool1, anchor='w', command = lambda: combined_callback2(frame_heatmap,frame_grafico1,entry_sampling_interval, entry_y_shift, frame_grafico_right))
     left_check1.grid(row=0, column=1, padx=10)
     
     notebook = ttk.Notebook(colonna_destra)
     notebook.pack(fill="both", expand=True)

     # Creazione del primo frame per la prima scheda del notebook
     stacks_tab1 = tk.Frame(notebook)
     notebook.add(stacks_tab1, text="Stacks")

     # Creazione del secondo frame per la seconda scheda del notebook
     lines_tab2 = tk.Frame(notebook)
     notebook.add(lines_tab2, text="Lines")
     
     notebook.bind("<<NotebookTabChanged>>", lambda event: reset_selected_lines())
     
     #stacks
     # Frame per il grafico
     frame_grafico_right = tk.Frame(stacks_tab1)
     frame_grafico_right.grid(row=1, column=0, sticky='nsew', padx=5,pady=5)
     
     
     # Frame per i controlli nella colonna destra
     frame_controls_right = tk.Frame(stacks_tab1)
     frame_controls_right.grid(row=0, column=0, sticky='nsew', padx=2,pady=2)
     
     # Frame aggiuntivo per i bottoni sotto il grafico nella colonna destra
     frame_lower_buttons_right = tk.Frame(stacks_tab1)
     frame_lower_buttons_right.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
     
     # Bottoni e checkbox nella colonna destra
     
     label_sampling = tk.LabelFrame(frame_controls_right,text="Sampling Intervall: ",bd=0, relief=tk.FLAT)
     label_sampling.grid(row=2, column=0,padx=5,pady=0, sticky="nsew")
     sampling_interval=tk.StringVar()
     entry_sampling_interval = tk.Entry(label_sampling,  textvariable=sampling_interval)
     entry_sampling_interval.grid(row=0, column=0,pady=1, sticky="w")
     entry_sampling_interval.insert(0, "5")  # Valore predefinito
     entry_sampling_interval.bind('<Return>',  lambda event: stacks_lines(sampling_interval, y2shift, frame_grafico_right, event)) #lambda con event serve nel bind nel caso di funzioni con argomento per chiamarle solo se necessario
     
     
     # Entry per lo shift in y
     label_y_shift = tk.LabelFrame(frame_controls_right, text="Shift in Y: ",bd=0, relief=tk.FLAT)
     label_y_shift.grid(row=2, column=1, padx=5, pady=0, sticky='nsew')
     y2shift=tk.StringVar()
     entry_y_shift = tk.Entry(label_y_shift, textvariable=y2shift)
     entry_y_shift.grid(row=0, column=0, pady=1,sticky="w")
     entry_y_shift.insert(0, "1000")  # Valore predefinito Sarebbe bello calcolare lo shift predefinito in base ai dati se no quando lo cambi è troppo piccolo
     entry_y_shift.bind('<Return>',  lambda event: stacks_lines(sampling_interval, y2shift, frame_grafico_right, event)) #lambda con event serve nel bind nel caso di funzioni con argomento per chiamarle solo se necessario
     
     
     #Lines
     # Frame per il grafico
     frame_grafico_right2 = tk.Frame(lines_tab2)
     frame_grafico_right2.grid(row=1, column=0, sticky='nsew', padx=5,pady=5)
     
     
     # Frame per i controlli nella colonna destra
     frame_controls_right2 = tk.Frame(lines_tab2)
     frame_controls_right2.grid(row=0, column=0, sticky='nsew', padx=2,pady=2)
     
     # Frame aggiuntivo per i bottoni sotto il grafico nella colonna destra
     frame_lower_buttons_right2 = tk.Frame(lines_tab2)
     frame_lower_buttons_right2.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
     
     # Entry per lo shift in y
     label_y_shift2 = tk.LabelFrame(frame_controls_right2, text="Shift in Y: ",bd=0, relief=tk.FLAT)
     label_y_shift2.grid(row=2, column=0, padx=5, pady=0, sticky='nsew')
     y2shift2=tk.StringVar()
     entry_y_shift2 = tk.Entry(label_y_shift2, textvariable=y2shift2)
     entry_y_shift2.grid(row=0, column=0, pady=1,sticky="w")
     entry_y_shift2.insert(0, "500")  # Valore predefinito Sarebbe bello calcolare lo shift predefinito in base ai dati se no quando lo cambi è troppo piccolo 
     entry_y_shift2.bind('<Return>',lambda event: plot_selected_lines(frame_grafico_right2,y2shift2,event) ) 
     
     
     back_button = tk.Button(frame_controls_right2, text="↩  Back", command=remove_last_selected_line)
     back_button.grid(row=2, column=2, padx=10, pady=0, sticky="e")
     
     reset_button = tk.Button(frame_controls_right2, text="↻  Reset", command=reset_selected_lines)
     reset_button.grid(row=2, column=3, padx=10, pady=0, sticky="e")

     # Configura il ridimensionamento dei frame dei grafici
     colonna_sinistra.grid_rowconfigure(1, weight=1)
     colonna_sinistra.grid_columnconfigure(0, weight=1)

     colonna_destra.grid_rowconfigure(1, weight=1)
     colonna_destra.grid_columnconfigure(0, weight=1)
     
     # Configurazione del ridimensionamento per le tabs
     lines_tab2.grid_rowconfigure(1, weight=1)
     lines_tab2.grid_columnconfigure(0, weight=1)
     
     # Configurazione del ridimensionamento per i frame dei controlli
     frame_controls_right2.grid_rowconfigure(0, weight=1)
     frame_controls_right2.grid_columnconfigure(0, weight=1)
     
     # Configurazione ridimensionamento dei frame per le tabs
     colonna_sinistra.grid_rowconfigure(1, weight=1)
     colonna_sinistra.grid_columnconfigure(0, weight=1)

     colonna_destra.grid_rowconfigure(1, weight=1)
     colonna_destra.grid_columnconfigure(0, weight=1)

     stacks_tab1.grid_rowconfigure(1, weight=1)
     stacks_tab1.grid_columnconfigure(0, weight=1)

     lines_tab2.grid_rowconfigure(1, weight=1)
     lines_tab2.grid_columnconfigure(0, weight=1)
     
     #inizialization
     if not (c2_entry_var.get() == "enter" or c2_entry_var.get() == "") :
         c2_binning(frame_heatmap)
         
     else:
         
         plot_image(frame_heatmap, spectra_image, "SpectraImage")
     
     if c2_bool1.get():
        left_check1.select()
        
     fig_empty, ax_empty = plt.subplots()
     ax_empty.set_xlabel('X')
     ax_empty.set_ylabel('Y')
     ax_empty.set_title('Select lines with right click')
     # Inserisci il grafico vuoto nel frame Tkinter
     canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico_right2)
     canvas.draw()
     toolbar = NavigationToolbar2Tk(canvas, frame_grafico_right2)
     toolbar.update()
     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
     
     stacks_lines(entry_sampling_interval, entry_y_shift, frame_grafico_right)
     
 def stacks_lines(sampling_interval, yshift, frame_grafico_right, event= None):
     """
     Function to plot the rows of the numpy array with the specified sampling interval and shift.
     """
     try:
         # Ottieni i valori inseriti dall'utente
         sampling_int = int(sampling_interval.get())
         y_shift = float(yshift.get())
         
         # Esegui il campionamento e plottaggio
         if sampling_int <= 0:
             raise ValueError("The sampling interval must be a positive number.")
         
         data=get_data_name()[0]
             
         
         num_rows = data.shape[0]
         x = np.arange(data.shape[1])  # Assegna un asse x per ogni colonna
         
         plt.figure(figsize=(8, 6))
         # Mantieni un accumulatore per lo shift cumulativo
         cumulative_y_shift = 0
        
         lines = []
        
         for i in range(0, num_rows, sampling_int):
            line, = plt.plot(x, data[i, :] + cumulative_y_shift, label=f'Line {i}', markersize=0.3)
            lines.append(line)
            cumulative_y_shift += y_shift  # Incrementa il valore cumulativo dello shift
      
         plt.xlabel('X')
         plt.title('Plot of lines stacks')
         plt.legend()
         
         # Visualizzazione del grafico nel frame
         for widget in frame_grafico_right.winfo_children():
             widget.destroy()  
         
         fig = plt.gcf()
         canvas = FigureCanvasTkAgg(fig, master=frame_grafico_right)
         canvas.draw()
         toolbar = NavigationToolbar2Tk(canvas, frame_grafico_right)
         toolbar.update()
         canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
         
         fig = plt.gcf()

         plt.close(fig) 
         
         # Configura il gestore di eventi per il click destro
         canvas.mpl_connect('button_press_event', lambda event: on_right_click(event, lines, frame_grafico_right,canvas))
       
    

     except ValueError as e:
         messagebox.showerror("Errore di input", str(e))
         

 def on_right_click(event, lines, frame_grafico_right,canvas):
     """
     Handler for right mouse click. Identifies the selected row and displays an Entry widget for modifications.
     """
     
     
     if event.button == 3:  # Click destro del mouse
         # Identifica la riga più vicina al punto di click
         for line in lines:
            if line.contains(event)[0]:
                # Mostra il menu contestuale
                show_context_menu(event, line, frame_grafico_right,canvas)
                break
  
 def show_context_menu(event, line, frame,canvas):
     """
     Shows a menu for modify the properties of the selected line
     """
     context_menu = tk.Menu(frame, tearoff=0)
     context_menu.add_command(label="X shift", command=lambda: shift1(line))
     context_menu.add_command(label="Factor multiplaier", command=lambda: corr_line(line))
     context_menu.add_separator()
     context_menu.add_command(label="Reset Graph", command=lambda: reset_line_properties(frame))
    
     # Usa il widget Tkinter del canvas Matplotlib per ottenere le coordinate root
     widget = canvas.get_tk_widget()
     canvas_x = widget.winfo_rootx() + event.x
     canvas_y = widget.winfo_rooty() + event.y
     
     # Posizionamento del menu nel punto corretto utilizzando le coordinate convertite
     context_menu.post(canvas_x, canvas_y)
     
     
 def shift1(line):
     """
     
     """
     shift_value = simpledialog.askfloat("Input", "Input the shift in X:", parent=new_window)
     x_data = line.get_xdata()  # Ottiene i dati X della linea
     y_data = line.get_ydata()  # Ottiene i dati Y della linea
    
     # Applica lo shift ai dati X
     x_data_shifted = x_data + shift_value
    
     # Aggiorna la linea con i nuovi dati X shiftati
     line.set_xdata(x_data_shifted)
     
     # Ridisegna il grafico per riflettere i cambiamenti
     line.figure.canvas.draw()

 def corr_line(line):
     """
     
     """
     factor = simpledialog.askfloat("Input", "Input the factor for the mpoltplication:",  parent=new_window)
     
     if factor is not None:
        y_data = line.get_ydata()  # Ottiene i dati Y della linea
        
        # Moltiplica i dati Y per il fattore specificato
        y_data_scaled = y_data * factor
        
        # Aggiorna la linea con i nuovi dati Y scalati
        line.set_ydata(y_data_scaled)
        
        # Forza il ridisegno degli assi per garantire che il grafico sia aggiornato
        ax = line.axes
        ax.relim()  # Ricalcola i limiti dei dati
        ax.autoscale_view()  # Applica la scala automatica in base ai nuovi dati

        # Ridisegna il grafico per riflettere i cambiamenti
        line.figure.canvas.draw()
     

 def reset_line_properties(frame):
     """
     Reset the lines properties at default values.
     """
     if frame == frame_grafico_right2 :
         plot_selected_lines(frame,y2shift2)
             
     else:
         stacks_lines(entry_sampling_interval, entry_y_shift, frame)
         
     
     
 #lines

 selected_lines = []  # Lista per memorizzare le righe selezionate

 def on_right_click2(event,data,title,frame_grafico_right2, y2shift2):
     """

     """
     if event.button == 3:  # Click destro del mouse
         if event.xdata is None or event.ydata is None:
             return  # Evita errori se il click è fuori dalla figura

         x, y = int(event.xdata), int(event.ydata)
         if 0 <= y < data.shape[0]:
             selected_lines.append(y)
             plot_selected_lines(frame_grafico_right2, y2shift2, event)
             plot_image(frame_heatmap,data,title)
   

 def plot_selected_lines(frame_grafico_right2,y2shift2, event=None):
    
     """
     Function that plot the selected lines from the heatmap frame.
     """
     if not selected_lines:
         return  # Nessuna riga selezionata
     try:        y_shift = float(y2shift2.get())
     
     except ValueError:
         y_shift = 0 

     # Crea un nuovo grafico per le righe selezionate
     fig_selected, ax_selected = plt.subplots()

     data=get_data_name()[0]   
     
     lines2 = []
     for i, line_index in enumerate(selected_lines):
        line, = ax_selected.plot(data[line_index, :] + i * y_shift, label=f'Line {line_index}')
        lines2.append(line)
    

     ax_selected.set_xlabel('X')
     ax_selected.set_ylabel('Y')
     ax_selected.legend()
     ax_selected.set_title('Selected lines from the Heatmap')

     # Pulisci il frame del grafico
     for widget in frame_grafico_right2.winfo_children():
         widget.destroy()

     # Inserisci il grafico aggiornato nel frame Tkinter
     canvas = FigureCanvasTkAgg(fig_selected, master=frame_grafico_right2)
     canvas.draw()
     toolbar = NavigationToolbar2Tk(canvas, frame_grafico_right2)
     toolbar.update()
     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
     
     canvas.mpl_connect('button_press_event', lambda event: on_right_click(event, lines2, frame_grafico_right2,canvas))

     plt.close(fig_selected)  # Chiudi la figura per evitare accumulo
     
     

     
 def reset_selected_lines():
     """
     Funzione per resettare la selezione delle righe e chiudere i grafici.
     """
     global selected_lines
     
     selected_lines = []
     plt.close('all')
     
     # Pulisce il frame del grafico
     for widget in frame_grafico_right2.winfo_children():
        widget.destroy()
        
        
     fig_empty, ax_empty = plt.subplots()
     ax_empty.set_xlabel('X')
     ax_empty.set_ylabel('Y')
     ax_empty.set_title('Select lines with right click')
     # Inserisci il grafico vuoto nel frame Tkinter
     canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico_right2)
     canvas.draw()
     toolbar = NavigationToolbar2Tk(canvas, frame_grafico_right2)
     toolbar.update()
     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
     
     data,name = get_data_name()
     plot_image(frame_heatmap, data, name)
 def remove_last_selected_line():
     """
     Rimuove l'ultima riga selezionata dalla lista e aggiorna il grafico.
     """
     global selected_lines  
     
     if selected_lines:
         # Rimuove l'ultima riga selezionata
         selected_lines.pop()
         
         # Aggiorna il grafico dopo la rimozione
         plot_selected_lines(frame_grafico_right2, y2shift2)
     else:
         pass
     data,name = get_data_name()
     plot_image(frame_heatmap, data, name)

 
 # Creazione della finestra principale
 root = tk.Toplevel(mainwindow)
 root.title("Spectra Analyser")
 root.geometry("1500x900+100+100")
 
 # Creazione della menubar
 menubar = tk.Menu(root)

 # Creazione del menu "File"
 file_menu = tk.Menu(menubar, tearoff=0)
 file_menu.add_command(label="Save", command=save_action)
 file_menu.add_command(label="Refresh", command=refresh_action)
 file_menu.add_separator()
 file_menu.add_command(label="Quit", command=quit_action)
 menubar.add_cascade(label="File", menu=file_menu)

 # Creazione del menu "Help"
 help_menu = tk.Menu(menubar, tearoff=0)

 # Creazione del sottomenu "Instructions"
 instructions_menu = tk.Menu(help_menu, tearoff=0)
 instructions_menu.add_command(label="Spectra Analyser")
 instructions_menu.add_command(label="Energy Calibration")

 # Aggiunge il sottomenu "Instructions" al menu "Help"
 help_menu.add_cascade(label="Instructions", menu=instructions_menu)

 # Aggiunge il comando "About" al menu "Help"
 help_menu.add_command(label="About...", command=about_action)

 # Aggiunge il menu "Help" alla menubar
 menubar.add_cascade(label="Help", menu=help_menu)

 # Configura la menubar
 root.config(menu=menubar)

 # Configura la menubar
 root.config(menu=menubar)

 # Creazione delle tre colonne
 colonna1 = tk.Frame(root)
 colonna1.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

 colonna2 = tk.Frame(root)
 colonna2.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

 colonna3 = tk.Frame(root)
 colonna3.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)

 # Frame aggiuntivi sotto le colonne 2 e 3 per i pulsanti
 frame_buttons2 = tk.Frame(root)
 frame_buttons2.grid(row=1, column=1, sticky='ew', padx=10, pady=10)

 frame_buttons3 = tk.Frame(root)
 frame_buttons3.grid(row=1, column=2, sticky='ew', padx=10, pady=10)

 ############################################################
 #LAYOUT OF THE MAIN WINDOW
 # COLONNA 1
 label_frame3 = tk.LabelFrame(colonna1, text="Enter the folder's path: ",bd=0, relief=tk.FLAT)
 label_frame3.pack(fill=tk.X)
 entrypath = ttk.Entry(label_frame3)
 entrypath.pack(side="left",pady=1)
 entrypath.insert(0, "enter")
 entrypath.bind('<Return>', folder)
 


 listbox_frame = tk.Frame(colonna1)
 listbox_frame.pack(fill=tk.BOTH, expand=True)

 scrollbar = tk.Scrollbar(listbox_frame)
 scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

 listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
 listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
 scrollbar.config(command=listbox.yview)
 listbox.bind('<<ListboxSelect>>', on_listbox_select)

 ############################################################

 # COLONNA 2
 # Widget sopra grafico colonna 2
 frame_conwidget1 = tk.Frame(colonna2)
 frame_conwidget1.pack(pady=2)

 # Frame per il grafico nella colonna 2
 frame_grafico1 = tk.Frame(colonna2)
 frame_grafico1.pack(fill=tk.BOTH, expand=True)

 label_frame = tk.LabelFrame(frame_conwidget1, text="Binning sets of n. lines: ",bd=0, relief=tk.FLAT)
 label_frame.pack(side="left", padx=10)
 c2_entry_var=tk.StringVar()
 c2_entry_bin = ttk.Entry(label_frame, textvariable=c2_entry_var)
 c2_entry_bin.pack( pady=1)
 c2_entry_bin.bind('<Return>',  lambda event: c2_binning(frame_grafico1, event)) #lambda con event serve nel bind nel caso di funzioni con argomento per chiamarle solo se necessario

 

 c2_bool1 = tk.BooleanVar()
 c2_check1 = tk.Checkbutton(frame_conwidget1, text="correctedNAccImage", variable=c2_bool1, anchor='w',command = lambda : c2_correction(frame_grafico1)) #lambda serve per chiamare la funzione solo quando necessario
 c2_check1.pack(side="left", padx=10)

 # Pulsante nella colonna 2
 button = tk.Button(frame_buttons2, text="Analyse heatmap", command=window_heatmap)
 button.pack(pady=5, side="left")

 ############################################################

 # COLONNA 3

 # Checkbox colonna 3
 frame_conwidget2 = tk.Frame(colonna3)
 frame_conwidget2.pack(pady=13.4)

 c3_bool1 = tk.IntVar(value=1)
 c3_check1 = tk.Checkbutton(frame_conwidget2, text="CurveCorrectedAcc", fg="black" ,variable=c3_bool1, anchor='n', command=plot_selected_graphs)
 c3_check1.pack(side=tk.LEFT, padx=10)

 c3_bool2 = tk.IntVar()
 c3_check2 = tk.Checkbutton(frame_conwidget2, text="baseAcc",fg="green", variable=c3_bool2, anchor='n',command=plot_selected_graphs)
 c3_check2.pack(side=tk.LEFT, padx=10)

 c3_bool3 = tk.IntVar()
 c3_check3 = tk.Checkbutton(frame_conwidget2, text="correctedAcc",fg="red", variable=c3_bool3, anchor='e',command=plot_selected_graphs)
 c3_check3.pack(side=tk.LEFT, padx=10)

 # Frame per il grafico nella colonna 3
 frame_grafico2 = tk.Frame(colonna3)
 frame_grafico2.pack(fill=tk.BOTH, expand=True)


 ############################################################

 # Configurazione delle righe e colonne per il ridimensionamento
 # Permette il ridimensionamento della finestra

 root.grid_columnconfigure(0, weight=1)
 root.grid_columnconfigure(1, weight=1)
 root.grid_columnconfigure(2, weight=1)
 root.grid_rowconfigure(0, weight=1)
 root.grid_rowconfigure(1, weight=0)  
 # Righe per i pulsanti
 colonna2.grid_rowconfigure(0, weight=1)
 colonna3.grid_rowconfigure(0, weight=1)

 ############################################################
 root.protocol("WM_DELETE_WINDOW", lambda: (root.quit(), root.destroy()))  # Ferma l'evento mainloop e chiude tutte le finestre
 

 # Starting of the mainloop
 root.mainloop()
 
