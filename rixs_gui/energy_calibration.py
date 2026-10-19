#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12  2024

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
from scipy.optimize import curve_fit
import datetime
from PIL import ImageGrab



def energy_calibration(mainwindow):
    
 
 global selected_data, selected_points
 
 class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window, ax):
        super().__init__(canvas, window)
        self.ax = ax  # Asse per aggiornare il grafico
        self.fitted_lines = []  # Lista per tracciare le linee di fit
        self.fitted_texts = []  # Lista per tracciare i testi dei parametri
        self.add_return_button()  # Aggiungi il pulsante Return alla toolbar

        # Aggiungi widget per l'intervallo sinistro (x_min)
        self.label_left = tk.Label(self, text="Left ")
        self.label_left.pack(side=tk.LEFT, padx=2, pady=1)

        self.entry_left = tk.Entry(self, width=7)
        self.entry_left.insert(0, 50)
        self.entry_left.pack(side=tk.LEFT, padx=2, pady=1)
        self.entry_left.bind('<Return>', self.update_interval)

        # Aggiungi widget per l'intervallo destro (x_max)
        self.label_right = tk.Label(self, text="Right ")
        self.label_right.pack(side=tk.LEFT, padx=2, pady=1)

        self.entry_right = tk.Entry(self, width=7)
        self.entry_right.insert(0, 50)
        self.entry_right.pack(side=tk.LEFT, padx=2, pady=1)
        self.entry_right.bind('<Return>', self.update_interval)

    def add_return_button(self):
        # Aggiungi il pulsante "Return" alla toolbar
        self.return_button = tk.Button(self, text="Return", command=self.remove_last_fit)
        self.return_button.pack(side=tk.RIGHT, padx=2, pady=1)

    def remove_last_fit(self):
        # Rimuovi l'ultima linea di fit
        if self.fitted_lines:
            line = self.fitted_lines.pop()  # Rimuovi l'ultima linea aggiunta
            line.remove()  # Rimuovi la linea dal grafico
            self.ax.figure.canvas.draw()

        # Rimuovi l'ultimo testo aggiunto
        if self.fitted_texts:
            text = self.fitted_texts.pop()  # Rimuovi l'ultimo testo aggiunto
            text.remove()  # Rimuovi il testo dal grafico
            self.ax.figure.canvas.draw()

    def update_interval(self, event=None):
        pass  # Qui puoi implementare la logica per aggiornare l'intervallo
 
 # Funzione per gestire il salvataggio
 def save_action():
    # Specifica il percorso e il nome del file dove salvare l'immagine
    save_path = "saved_window_image.png"  # Puoi cambiare il percorso e il nome del file qui
    
    # Ottieni la posizione della finestra Tkinter
    x = wind.winfo_rootx()
    y = wind.winfo_rooty()
    width = wind.winfo_width()
    height = wind.winfo_height()
    
    # Cattura l'immagine della finestra
    ImageGrab.grab((x, y, x + width, y + height)).save(save_path)

    messagebox.showinfo("Save", f"Window saved as {save_path}.")

 # Funzione per gestire il refresh
 def refresh_action():
     
    # Chiudi la finestra corrente
    wind.quit()  # Chiude l'applicazione Tkinter
    wind.destroy()  # Distrugge la finestra corrente
    energy_calibration(mainwindow)
    

 # Funzione per gestire l'uscita
 def quit_action():
    # Chiudi la finestra corrente
    wind.quit()  # Chiude l'applicazione Tkinter
    wind.destroy()  # Distrugge la finestra corrente

 # Funzione per la sezione "About"
 def about_action():
     # Create a Toplevel window
     presentation_window = tk.Toplevel(wind)
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
 
 # Definizione della funzione gaussiana per il fit
 def gaussian(x, amp, mean, sigma):
    return amp * np.exp(-(x - mean) ** 2 / (2 * sigma ** 2))
 
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
          
     
 selected_data = {}

 def on_listbox_select(event=None):
    """
    Handles the selection of a file in the listbox, colors the selected item, and appends
    the correctedAcc dataset of the selected file to a list.
    """
    selected_indices = listbox.curselection()  # Get selected indices
    folder_path = entrypath.get()  # Get folder path from entry
    
    file_name = listbox.get(selected_indices[-1])
    file_path = os.path.join(folder_path, file_name)
    
    corrected_acc = handle_file(file_path)
    selected_data[file_name] = corrected_acc
    
    plot_selected_files()
        

    

 def handle_file(path):
    """
    Opens the selected .hdf5 file and retrieves the correctedAcc dataset.
    """
    with h5py.File(path, 'r') as file:
        try:
            corrected_acc = file["HistogramCorrected"][:] 
        except:
            corrected_acc = file["correctedAcc"][:]  # Load the dataset
    return corrected_acc
         
     #initialization
     
 def reset_files():
      """
      Funzione per resettare la selezione delle righe e chiudere i grafici.
      """
      global selected_data
      
      selected_data = {}
      plt.close('all')
      
      # Ripristina il colore bianco per tutte le caselle nella listbox
      for i in range(listbox.size()):  # listbox.size() ritorna il numero di elementi nella listbox
        listbox.selection_clear(i)
      
      
     
         
      for widget in frame_grafico1.winfo_children():
         widget.destroy()
         
      fig_empty, ax_empty = plt.subplots()
      ax_empty.set_xlabel('CCD position (pixel)')
      ax_empty.set_ylabel('Y')
      ax_empty.set_title('Select files')
      canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico1)
      canvas.draw()
      toolbar = NavigationToolbar2Tk(canvas, frame_grafico1)
      toolbar.update()
      canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
         
      
      
 def remove_last_selected_file():
    """
    Rimuove l'ultima riga selezionata dalla lista, aggiorna il grafico e 
    resetta il colore dell'ultima casella selezionata nella listbox.
    """
    global selected_data
    
    if selected_data:
        
      if len(selected_data.items())==1:
          reset_files()
      else :
        # Rimuovi l'ultimo file selezionato
        last_file_name = list(selected_data.keys())[-1]  # Ottieni l'ultimo file
        del selected_data[last_file_name]  # Rimuovi il file dal dizionario
        
        # Trova l'indice dell'ultima casella selezionata nella listbox
        selected_indices = listbox.curselection()
        
        if selected_indices:
            last_selected_index = selected_indices[-1]  # Ottieni l'ultimo indice selezionato
            
            # Deseleziona la casella per rimuovere la selezione visiva
            listbox.selection_clear(last_selected_index)
        
        # Aggiorna il grafico dopo la rimozione
            
        plot_selected_files()
    else:
        pass
         
 def plot_selected_files():
    
     """
     Function that plot the selected files
     """
     if not selected_data:
        return  # Nessun dato selezionato

     # Crea un nuovo grafico per le righe selezionate
     fig_selected, ax_selected = plt.subplots()

     ax_selected.set_xlabel('CCD position (pixel)')
     ax_selected.set_ylabel('Y')
     ax_selected.set_title('Selected CurveAcc from files list')

     # Pulisci il frame del grafico
     for widget in frame_grafico1.winfo_children():
        widget.destroy()

   
     for i, (file_name, data) in enumerate(selected_data.items()):
         x = np.arange(len(data))  # Assumi che l'asse x sia basato sull'indice degli array
         ax_selected.plot(x, data, label=f'{file_name}')
         
     ax_selected.legend(fontsize='small')

    # Inserisci il grafico aggiornato nel frame Tkinter
     canvas = FigureCanvasTkAgg(fig_selected, master=frame_grafico1)
     canvas.draw()
     toolbar = CustomToolbar(canvas, frame_grafico1, ax_selected)
     toolbar.update()
     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
     
     canvas.mpl_connect('button_press_event', lambda event: right_click(event, ax_selected,toolbar))

     plt.close(fig_selected) 
 
 selected_points=[]
 curve_energy={}
   
 def right_click(event, ax, toolbar):
    global curve_energy
    if varRB.get() == 1:
        if event.button == 3:  # Verifica che sia stato fatto il clic destro
            x_coord = event.xdata  # Ottieni la coordinata x dove si è clickato

            if x_coord is not None:  # Se la coordinata x è valida
                y_energy = simpledialog.askfloat("Input", f"Insert the energy for x = {x_coord:.2f}:", parent=wind)

                if y_energy is not None:
                    # Aggiungi le coordinate alla lista
                    selected_points.append((x_coord, y_energy))

                    # Ridisegna il grafico con i punti nel secondo frame
                    update_fit_plot()

    elif varRB.get() == 0:
        if event.button == 3:  # Verifica che sia stato fatto il clic destro
            x_coord = event.xdata  # Ottieni la coordinata x dove si è cliccato

            if x_coord is not None:  # Se la coordinata x è valida
                y_energy = simpledialog.askfloat("Input", f"Insert the energy for x = {x_coord:.2f}:", parent=wind)
                if y_energy is not None:
                    try:
                        # Ottieni i valori inseriti per l'intervallo da entry_left e entry_right
                        left_bound = float(toolbar.entry_left.get())
                        right_bound = float(toolbar.entry_right.get())
                    except ValueError:
                        tk.messagebox.showerror("Input Error", "Please enter valid numbers for the bounds.")
                        return

                    # Cerca la linea più vicina al punto cliccato
                    for line in ax.lines:
                        contains, _ = line.contains(event)
                        if contains:  # Se la linea contiene il punto cliccato
                            x_data = line.get_xdata()
                            y_data = line.get_ydata()

                            # Seleziona i punti nel range [x0 - entry_left, x0 + entry_right]
                            mask = (x_data >= x_coord - left_bound) & (x_data <= x_coord + right_bound)
                            x_selected = x_data[mask]
                            y_selected = y_data[mask]

                            if len(x_selected) > 0:  # Procedi solo se ci sono punti validi
                                fit_gaussian(x_selected, y_selected, x_coord, ax, y_energy, toolbar)
                                break  # Esci dal ciclo dopo aver trovato la linea giusta

 def fit_gaussian(x_selected, y_selected, x0, ax, y_energy, toolbar):
    # Stima iniziale per il fit gaussiano
    initial_guess = [max(y_selected), x0, 10.0]  # [ampiezza, posizione centrale, sigma]

    try:
        # Esegui il fit gaussiano
        popt, _ = curve_fit(gaussian, x_selected, y_selected, p0=initial_guess)
        amp, mean, sigma = popt

        # (centro curva gaussiana, energia inserita)
        point = (mean, y_energy)

        # Aggiungi il punto massimo alla lista dei punti selezionati
        selected_points.append(point)

        # Aggiorna il grafico
        update_fit_plot()

        # Genera i valori x per plottare il fit
        x_fit = np.linspace(min(x_selected), max(x_selected), 500)
        y_fit = gaussian(x_fit, *popt)

        # Plotta la curva del fit sull'asse esistente e salva la linea
        line, = ax.plot(x_fit, y_fit, label=f'Fit at {mean:.2f}')
        toolbar.fitted_lines.append(line)  # Aggiungi la linea alla lista nel toolbar

        # Visualizza i coefficienti del fit sul grafico e salva il testo
        text_position = (0.05, 0.95)  # Posizione in percentuale (x, y) sull'asse
        text = ax.text(
            text_position[0], text_position[1], 
            f'Fit Gaussian:\nAmplitude: {amp:.2f}\nMean (μ): {mean:.2f}\nSigma (σ): {sigma:.2f}',
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7)
        )
        toolbar.fitted_texts.append(text)  # Aggiungi il testo alla lista nel toolbar

        # Aggiorna il grafico
        ax.figure.canvas.draw()

    except RuntimeError as e:
        messagebox.showerror("Fit Error", f"Unable to perform Gaussian fit: {e}")
        
 def update_fit_plot():
     # Pulisci il frame_grafico2 e crea un nuovo grafico vuoto
   for widget in frame_grafico2.winfo_children():
       widget.destroy()

   # Crea una nuova figura per il secondo grafico
   fig_empty, ax_empty = plt.subplots()
   ax_empty.set_xlabel('CCD position (pixel)')
   ax_empty.set_ylabel('Excitation energy (eV)')
   ax_empty.set_title('Points plotted from right-clicks')

   # Disegna i punti salvati
   if selected_points:
       x_coords, y_coords = zip(*selected_points)
       ax_empty.plot(x_coords, y_coords, 'ro')  # 'ro' indica i punti rossi

   # Inserisci il grafico aggiornato nel frame Tkinter
   canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico2)
   canvas.draw()
   toolbar = NavigationToolbar2Tk(canvas, frame_grafico2)
   toolbar.update()
   canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
   
 def reset_points():
     global selected_points
     
     selected_points = []
     plt.close('all')
     
     for widget in frame_grafico2.winfo_children():
        widget.destroy()
     
     fig_empty, ax_empty = plt.subplots()
     ax_empty.set_xlabel('CCD position (pixel)')
     ax_empty.set_ylabel('Excitetion energy (eV)')
     ax_empty.set_title('Right click on the curve to set a point')
     # Inserisci il grafico vuoto nel frame Tkinter
     canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico2)
     canvas.draw()
     toolbar = NavigationToolbar2Tk(canvas, frame_grafico2)
     toolbar.update()
     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
     
     
 def back_points():
     global selected_points
     
     if selected_points:
       selected_points.pop()
       update_fit_plot()
     else:
         pass
 def history():
     # Nome del file di output
    file_name = "fit_results.txt"
    
    try:
        # Leggi il contenuto del file
        with open(file_name, 'r') as file:
            file_content = file.read()
            
        # Crea una nuova finestra per visualizzare la storia del fit
        history_window = tk.Toplevel()
        history_window.title("Fit History")
        
        # Crea un frame per contenere sia la Text che la Scrollbar
        frame = tk.Frame(history_window)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Crea un widget Text per visualizzare il contenuto del file
        text_widget = tk.Text(frame, wrap='word', width=80, height=20)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crea una scrollbar verticale e collegala al widget Text
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Collega la scrollbar al widget Text
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Inserisci il contenuto del file nel widget Text
        text_widget.insert(tk.END, file_content)
        
        # Disabilita il widget Text per renderlo di sola lettura
        text_widget.config(state=tk.DISABLED)
        
    except FileNotFoundError:
        # Mostra un messaggio di errore se il file non esiste
        messagebox.showerror("Error", f"The file '{file_name}' was not found.")
 
 def gaus_graphs():
     pass
 
 def fitgaus():
    global a,b,c
    # Estrai le coordinate x e y dalla lista di tuple
    x_coords, y_coords = zip(*selected_points)
    
    
    
    # Esegui il fit polinomiale del secondo ordine
    coefficients = np.polyfit(x_coords, y_coords, 2)
    a, b, c = coefficients
    
    # Crea la funzione polinomiale da usare per plottare
    polynomial = np.poly1d(coefficients)
    
    # Genera i valori x e y per la curva approssimata
    x_fit = np.linspace(min(x_coords), max(x_coords), 100)
    y_fit = polynomial(x_fit)
    
    for widget in frame_grafico2.winfo_children():
        widget.destroy()

    # Crea una nuova figura per il secondo grafico
    fig_empty, ax_empty = plt.subplots()
    ax_empty.set_xlabel('CCD position (pixel)')
    ax_empty.set_ylabel('Excitation energy (eV)')
    ax_empty.set_title('Points plotted from right-clicks')

    # Disegna i punti salvati
    if selected_points:
        x_coords, y_coords = zip(*selected_points)
        ax_empty.plot(x_coords, y_coords, 'ro')  # 'ro' indica i punti rossi

    # Inserisci il grafico aggiornato nel frame Tkinter
    canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico2)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, frame_grafico2)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Plotta la curva del fit sull'asse esistente
    ax_empty.plot(x_fit, y_fit, color='red', label=f'Fit: y = {c:.3f} + {b:.3f}x + {a:.3f}x²')
    
    # Visualizza i coefficienti direttamente sul grafico
    text_position = (0.05, 0.95)  # Posizione in percentuale (x, y) delle coordinate dell'asse
    ax_empty.text(
        text_position[0], text_position[1], 
        f'Coefficient a: {a:.4e}\nCoefficient b: {b:.4e}\nCoefficient c: {c:.4e}',
        transform=ax_empty.transAxes, fontsize=12, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7)
    )
    
    # Aggiorna il grafico
    ax_empty.legend()
    ax_empty.figure.canvas.draw()
    
    # Salva i risultati del fit in un file
    file_name = "fit_results.txt"  # Nome del file di output
    with open(file_name, 'a') as file:  # Apri il file in modalità 'append'
      current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      file.write(f"Fit results {current_time} :\n")
      file.write(f"Coefficient a: {a:.10e}\n")
      file.write(f"Coefficient b: {b:.10e}\n")
      file.write(f"Coefficient c: {c:.10e}\n")
      file.write("Points used for the fit:\n")
      for (x, y) in selected_points:
          file.write(f"({x}, {y})\n")
      file.write("-" * 30 + "\n")  # Divider per separare i risultati dei diversi fit
 def check():
    
    # Creazione di una finestra Toplevel
    top = tk.Toplevel(wind)
    top.title("Energy Calibration Result")

    # Creazione della figura Matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plotta ogni dataset
    for file_name, data in selected_data.items():
        x_pixels = np.arange(len(data))  # Ascisse dei pixel
        energies = a * x_pixels**2 + b * x_pixels + c  # Conversione pixel -> energia

        ax.plot(energies, data, label=f"{file_name}")

    # Aggiunge le etichette e il titolo
    ax.set_xlabel("Excitation energy (eV)")
    ax.set_ylabel("Y")
    ax.set_title("Energy Calibration Result")
    ax.legend(fontsize="small")

    # Creazione della toolbar per il grafico
    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Aggiunge la toolbar
    toolbar_frame = tk.Frame(top)
    toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

    # Mostra il canvas
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    
 wind = tk.Toplevel(mainwindow)
 wind.title("Energy Calibration")
 wind.geometry("1500x900+100+100")
 
 # Creazione della menubar
 menubar = tk.Menu(wind)

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
 wind.config(menu=menubar)
 
 # Creazione delle tre colonne
 colonna1 = tk.Frame(wind)
 colonna1.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

 colonna2 = tk.Frame(wind)
 colonna2.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

 colonna3 = tk.Frame(wind)
 colonna3.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)

 # Frame aggiuntivi sotto le colonne 2 e 3 per i pulsanti
 frame_buttons2 = tk.Frame(wind)
 frame_buttons2.grid(row=1, column=1, sticky='ew', padx=10, pady=2)

 frame_buttons3 = tk.Frame(wind)
 frame_buttons3.grid(row=1, column=2, sticky='ew', padx=10, pady=2)

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

 # Modifica `selectmode` a `tk.EXTENDED` per abilitare il trascinamento
 listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED)
 listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
 scrollbar.config(command=listbox.yview)

 # Associa l'evento di selezione multipla alla funzione `on_listbox_select`
 listbox.bind('<<ListboxSelect>>', on_listbox_select)

 ############################################################

 # COLONNA 2
 # Widget sopra grafico colonna 2
 frame_conwidget1 = tk.Frame(colonna2)
 frame_conwidget1.pack(pady=5)
 
 # Creazione di un LabelFrame per avvolgere i bottoni con il titolo "Files"
 label_frame_files = tk.LabelFrame(frame_conwidget1, text="  Files", bd=0, relief=tk.FLAT)
 label_frame_files.pack(side=tk.LEFT, padx=0, pady=6)

 # Bottone "Back"
 back = tk.Button(label_frame_files, text="↩  Back", command=remove_last_selected_file)
 back.pack(side=tk.LEFT, padx=(0, 5), pady=2)

 # Bottone "Reset"
 reset = tk.Button(label_frame_files, text="↻  Reset", command=reset_files)
 reset.pack(side=tk.LEFT, padx=(5, 30), pady=2)
 
 varRB = tk.IntVar()
 
 selectionRB = tk.Radiobutton(frame_conwidget1, text="Selection", variable=varRB, value=1)
 selectionRB.pack(side=tk.RIGHT, padx=(0,1), pady=10)
 

 fitgausRB = tk.Radiobutton(frame_conwidget1, text="FitGaus",  variable=varRB, value=0)
 fitgausRB.pack(side=tk.RIGHT, padx=(40,0), pady=10)
 

 frame_grafico1 = tk.Frame(colonna2)
 frame_grafico1.pack(fill=tk.BOTH, expand=True)
 
 fig_empty, ax_empty = plt.subplots()
 ax_empty.set_xlabel('CCD position (pixel)')
 ax_empty.set_ylabel('Y')
 ax_empty.set_title('Select files')
 # Inserisci il grafico vuoto nel frame Tkinter
 canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico1)
 canvas.draw()
 toolbar = NavigationToolbar2Tk(canvas, frame_grafico1)
 toolbar.update()
 canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
 
 #bottone sotto colonna 2 
 button = tk.Button(frame_buttons2, text="Graphs Gaussian Parameters")
 button.pack(pady=(5,10), side="left")
 
 


 ############################################################

 # COLONNA 3

 # Checkbox colonna 3
 frame_conwidget2 = tk.Frame(colonna3)
 frame_conwidget2.pack(pady=5)


 fit_button = tk.Button(frame_conwidget2, text="Fit dispersion", fg="black" ,width="30", command=fitgaus)
 fit_button.pack(side=tk.LEFT, padx=10, pady=10)
 
 label_frame_points = tk.LabelFrame(frame_conwidget2, text="  Points", bd=0, relief=tk.FLAT)
 label_frame_points.pack(side=tk.LEFT, padx=10, pady=6)

 # Bottone "Back"
 back2 = tk.Button(label_frame_points, text="↩  Back", command=back_points)
 back2.pack(side=tk.LEFT, padx=(0,5), pady=2)

 # Bottone "Reset"
 reset2 = tk.Button(label_frame_points, text="↻  Reset", command=reset_points)
 reset2.pack(side=tk.LEFT, padx=(5,0), pady=2)
 
 check_button = tk.Button(frame_buttons3, text="Check", command=check)
 check_button.pack(side="left")
 
 
 
 #bottone sotto colonna 3
 history_button = tk.Button(frame_buttons3, text="History", fg="black" ,width="5", height="2", command=history)
 history_button.pack(side="right", padx=20, pady=(0,10))
 


 # Frame per il grafico nella colonna 3
 frame_grafico2 = tk.Frame(colonna3)
 frame_grafico2.pack(fill=tk.BOTH, expand=True)
 
 fig_empty, ax_empty = plt.subplots()
 ax_empty.set_xlabel('CCD position (pixel)')
 ax_empty.set_ylabel('Excitetion energy (eV)')
 ax_empty.set_title('Right click on the curve to set a point')
 # Inserisci il grafico vuoto nel frame Tkinter
 canvas = FigureCanvasTkAgg(fig_empty, master=frame_grafico2)
 canvas.draw()
 toolbar = NavigationToolbar2Tk(canvas, frame_grafico2)
 toolbar.update()
 canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

 ############################################################

 # Configurazione delle righe e colonne per il ridimensionamento
 # Permette il ridimensionamento della finestra

 wind.grid_columnconfigure(0, weight=1)
 wind.grid_columnconfigure(1, weight=1)
 wind.grid_columnconfigure(2, weight=1)
 wind.grid_rowconfigure(0, weight=1)
 wind.grid_rowconfigure(1, weight=0)  
 # Righe per i pulsanti
 colonna2.grid_rowconfigure(0, weight=1)
 colonna3.grid_rowconfigure(0, weight=1)

 ############################################################
 wind.protocol("WM_DELETE_WINDOW", lambda: (wind.quit(), wind.destroy()))  # Ferma l'evento mainloop e chiude tutte le finestre
 
 
 # Starting of the mainloop
 wind.mainloop()
 
