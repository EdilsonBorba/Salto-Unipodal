# usando interface Tkinter para selecionar os arquivos

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# Função para selecionar arquivo
def select_file(label):
    file_path = filedialog.askopenfilename()
    if file_path:
        label.config(text=file_path)

# Função para selecionar pasta
def select_folder(label):
    folder_path = filedialog.askdirectory()
    if folder_path:
        label.config(text=folder_path)

# Função para ler arquivo .sto e transformá-lo em DataFrame
def read_sto_to_dataframe(file_path, header_lines):
    with open(file_path, 'r') as file:
        lines = file.readlines()[header_lines:]
    data = [line.strip().split() for line in lines]
    return pd.DataFrame(data)

# Função para aplicar o filtro Butterworth
def butter_lowpass_filter(data, fc, fs, order):
    w = fc / (fs / 2)
    b, a = signal.butter(order, w, 'low')
    return signal.filtfilt(b, a, data)

# Função para executar a análise
def run_analysis():
    NAME = name_entry.get()
    TRIAL = trial_entry.get()
    LEG = leg_var.get()
    FILE_OUTPUT = output_folder_label.cget("text")
    FILE_PATH_ANGLES = angles_file_label.cget("text")
    FILE_PATH_MARKER = marker_file_label.cget("text")
    CUTOFF = 4  # Frequência de corte do filtro
    ORDER = 2  # Ordem do filtro
    THRESHOLD_CHANGE = 0.005  # Limiar de mudança para identificar o despregue e retorno ao solo

    if not all([NAME, TRIAL, LEG, FILE_OUTPUT, FILE_PATH_ANGLES, FILE_PATH_MARKER]):
        messagebox.showwarning("Input Missing", "Todos os campos precisam ser preenchidos.")
        return

    try:
        # Leitura dos arquivos de ângulos e marcadores
        data_angles = read_sto_to_dataframe(FILE_PATH_ANGLES, header_lines=11)
        data_marker = read_sto_to_dataframe(FILE_PATH_MARKER, header_lines=6)

        # Conversão para arrays numpy
        data_marker = np.array(data_marker)
        data_angles = np.array(data_angles)

        time = data_angles[:, 0].astype(float)
        frame = data_marker[:, 0].astype(float)
        fsample = 1 / (time[2] - time[1])
        dt_kinematic = 1 / fsample

        # Aplicando o filtro de Butterworth
        filtered_data_angle = np.zeros_like(data_angles)
        for col in range(data_angles.shape[1]):
            filtered_data_angle[:, col] = butter_lowpass_filter(data_angles[:, col].astype(float), CUTOFF, fsample, ORDER)

        data_angles = filtered_data_angle

        filtered_data_marker = np.zeros_like(data_marker)
        for col in range(data_marker.shape[1]):
            filtered_data_marker[:, col] = butter_lowpass_filter(data_marker[:, col].astype(float), CUTOFF, fsample, ORDER)

        data_marker = filtered_data_marker

        # Seleção dos ângulos e marcadores com base na perna
        if LEG == 'Direita':
            hip_flexion = data_angles[:, 7]
            knee_flexion = data_angles[:, 10]
            ankle_flexion = data_angles[:, 12]
            toe_x = data_marker[:, 53]
            toe_y = data_marker[:, 54]
            heel_x = data_marker[:, 59]
            heel_y = data_marker[:, 60]
        else:
            hip_flexion = data_angles[:, 15]
            knee_flexion = data_angles[:, 18]
            ankle_flexion = data_angles[:, 20]
            toe_x = data_marker[:, 44]
            toe_y = data_marker[:, 45]
            heel_x = data_marker[:, 50]
            heel_y = data_marker[:, 51]

        pelvis_ty = data_angles[:, 5]

        # Calculando a mudança nas posições X e Y entre frames
        delta_toe_x = np.diff(toe_x)
        delta_toe_y = np.diff(toe_y)
        delta_heel_x = np.diff(heel_x)
        delta_heel_y = np.diff(heel_y)

        # Identificação do momento de despregue e retorno ao solo
        momento_despregue = None
        momento_retorno_solo = None

        for i in range(1, len(delta_toe_x)):
            change = np.sqrt(delta_toe_x[i]**2 + delta_toe_y[i]**2)
            if change > THRESHOLD_CHANGE:
                momento_despregue = i
                break

        for i in range(momento_despregue, len(delta_toe_x)):
            change = np.sqrt(delta_toe_x[i]**2 + delta_toe_y[i]**2)
            if change < THRESHOLD_CHANGE:
                momento_retorno_solo = i
                parte_aterrissagem = "Calcanhar" if delta_heel_y[i] < delta_toe_y[i] else "Ponta do Pé"
                break

        # Cálculo das métricas
        tempo_aereo = (momento_retorno_solo - momento_despregue) * dt_kinematic
        altura_pelvis_pre = pelvis_ty[momento_despregue]
        altura_pelvis_pos = pelvis_ty[momento_retorno_solo]
        altura_max_pelvis = np.max(pelvis_ty[momento_despregue:momento_retorno_solo])
        diff_altura_max_pelvis = altura_max_pelvis - min(altura_pelvis_pre, altura_pelvis_pos)
        dist_inicial = toe_x[momento_despregue]
        dist_final = toe_x[momento_retorno_solo]
        distance = dist_final - dist_inicial

        # Métricas Pré e Pós salto
        start_pre = max(momento_despregue - int(1 / dt_kinematic), 0)
        end_pre = momento_despregue

        hip_pre_max = np.max(hip_flexion[start_pre:end_pre])
        hip_pre_min = np.min(hip_flexion[start_pre:end_pre])
        hip_pre_amplitude = hip_pre_max - hip_pre_min

        start_pos = momento_retorno_solo
        end_pos = min(momento_retorno_solo + int(3 / dt_kinematic), len(hip_flexion))

        hip_pos_max = np.max(hip_flexion[start_pos:end_pos])
        hip_pos_min = np.min(hip_flexion[start_pos:end_pos])
        hip_pos_amplitude = hip_pos_max - hip_pos_min

        knee_pre_max = np.max(knee_flexion[start_pre:end_pre])
        knee_pre_min = np.min(knee_flexion[start_pre:end_pre])
        knee_pre_amplitude = knee_pre_max - knee_pre_min

        ankle_pre_max = np.max(ankle_flexion[start_pre:end_pre])
        ankle_pre_min = np.min(ankle_flexion[start_pre:end_pre])
        ankle_pre_amplitude = ankle_pre_max - ankle_pre_min

        knee_pos_max = np.max(knee_flexion[start_pos:end_pos])
        knee_pos_min = np.min(knee_flexion[start_pos:end_pos])
        knee_pos_amplitude = knee_pos_max - knee_pos_min

        ankle_pos_max = np.max(ankle_flexion[start_pos:end_pos])
        ankle_pos_min = np.min(ankle_flexion[start_pos:end_pos])
        ankle_pos_amplitude = ankle_pos_max - ankle_pos_min

        # Criar DataFrame com os dados
        df_export_data = pd.DataFrame({
            'Nome': [NAME],
            'Perna': [LEG],
            'Tentativa': [TRIAL],
            'Distância (m)': [distance],
            'Tempo Aéreo (s)': [tempo_aereo],
            'Diferença máxima altura pélvica (m)': [diff_altura_max_pelvis],
            'Aterrissagem': [parte_aterrissagem],
            'Joelho Flexão Máxima Pré (°)': [knee_pre_max],
            'Joelho Flexão Mínima Pré (°)': [knee_pre_min],
            'Joelho Amplitude Pré (°)': [knee_pre_amplitude],
            'Quadril Flexão Máxima Pré (°)': [hip_pre_max],
            'Quadril Extensão Máxima Pré (°)': [hip_pre_min],
            'Quadril Amplitude Pré (°)': [hip_pre_amplitude],
            'Tornozelo Dorsiflexão Pré (°)': [ankle_pre_max],
            'Tornozelo Plantiflexão Pré (°)': [ankle_pre_min],
            'Tornozelo Amplitude Pré (°)': [ankle_pre_amplitude],
            'Joelho Flexão Máxima Pós (°)': [knee_pos_max],
            'Joelho Flexão Mínima Pós (°)': [knee_pos_min],
            'Joelho Amplitude Pós (°)': [knee_pos_amplitude],
            'Quadril Flexão Máxima Pós (°)': [hip_pos_max],
            'Quadril Extensão Máxima Pós (°)': [hip_pos_min],
            'Quadril Amplitude Pós (°)': [hip_pos_amplitude],
            'Tornozelo Dorsiflexão Máxima Pós (°)': [ankle_pos_max],
            'Tornozelo Plantiflexão Máxima Pós (°)': [ankle_pos_min],
            'Tornozelo Amplitude Pós (°)': [ankle_pos_amplitude],
        })

        # Salvar os dados no Excel
        excel_filename = os.path.join(FILE_OUTPUT, f"{NAME}_{LEG}_Teste{TRIAL}_Resultados.xlsx")
        df_export_data.to_excel(excel_filename, index=False)
        print(f"Resultados salvos em {excel_filename}")

        # Gráfico
        tempo = np.arange(0, len(toe_y)) * dt_kinematic
        tempo_inicial = max(0, momento_despregue - int(0.1 / dt_kinematic))
        tempo_final = min(len(tempo), momento_retorno_solo + int(0.1 / dt_kinematic))

        plt.figure(figsize=(14, 3))
        plt.plot(tempo[tempo_inicial:tempo_final], toe_y[tempo_inicial:tempo_final], label='Ponta do Pé', color='blue')
        plt.plot(tempo[tempo_inicial:tempo_final], heel_y[tempo_inicial:tempo_final], label='Calcanhar', color='green')

        plt.scatter(tempo[momento_despregue], toe_y[momento_despregue], color='red', label='Despregue (Ponta do pé)', zorder=5)
        plt.axvline(x=tempo[momento_despregue], color='red', linestyle='--', label='Momento de Despregue')

        if parte_aterrissagem == "Calcanhar":
            plt.scatter(tempo[momento_retorno_solo], heel_y[momento_retorno_solo], color='orange', label=f'Retorno ao Solo ({parte_aterrissagem})', zorder=5)
            plt.axvline(x=tempo[momento_retorno_solo], color='orange', linestyle='--', label='Momento de Retorno')
        else:
            plt.scatter(tempo[momento_retorno_solo], toe_y[momento_retorno_solo], color='orange', label=f'Retorno ao Solo ({parte_aterrissagem})', zorder=5)
            plt.axvline(x=tempo[momento_retorno_solo], color='orange', linestyle='--', label='Momento de Retorno')

        plt.title('Posição ao Longo do Tempo')
        plt.xlabel('Tempo (segundos)')
        plt.ylabel('Posição Vertical (m)')
        plt.legend()
        plt.grid(True)

        # Salvar o gráfico
        image_filename = os.path.join(FILE_OUTPUT, f"{NAME}_{LEG}_Teste{TRIAL}_Grafico.png")
        plt.savefig(image_filename, dpi=1200)
        print(f"Gráfico salvo em {image_filename} com 1200 dpi")
        plt.show()

        messagebox.showinfo("Sucesso", "Análise concluída e resultados salvos com sucesso!")
    
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Interface Gráfica com Tkinter
root = tk.Tk()
root.title("Análise de Dados Biomecânicos")

# Nome
tk.Label(root, text="Nome:").grid(row=0, column=0, sticky='e')
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

# Tentativa
tk.Label(root, text="Tentativa:").grid(row=1, column=0, sticky='e')
trial_entry = tk.Entry(root)
trial_entry.grid(row=1, column=1)

# Seleção da Perna
tk.Label(root, text="Perna:").grid(row=2, column=0, sticky='e')
leg_var = tk.StringVar()
tk.Radiobutton(root, text="Direita", variable=leg_var, value="Direita").grid(row=2, column=1, sticky='w')
tk.Radiobutton(root, text="Esquerda", variable=leg_var, value="Esquerda").grid(row=2, column=2, sticky='w')

# Arquivo de Ângulos
tk.Label(root, text="Arquivo de Ângulos:").grid(row=3, column=0, sticky='e')
angles_file_label = tk.Label(root, text="Nenhum arquivo selecionado", anchor="w")
angles_file_label.grid(row=3, column=1)
angles_button = tk.Button(root, text="Selecionar", command=lambda: select_file(angles_file_label))
angles_button.grid(row=3, column=2)

# Arquivo de Marcadores
tk.Label(root, text="Arquivo de Marcadores:").grid(row=4, column=0, sticky='e')
marker_file_label = tk.Label(root, text="Nenhum arquivo selecionado", anchor="w")
marker_file_label.grid(row=4, column=1)
marker_button = tk.Button(root, text="Selecionar", command=lambda: select_file(marker_file_label))
marker_button.grid(row=4, column=2)

# Pasta de Saída
tk.Label(root, text="Pasta de Saída:").grid(row=5, column=0, sticky='e')
output_folder_label = tk.Label(root, text="Nenhuma pasta selecionada", anchor="w")
output_folder_label.grid(row=5, column=1)
output_folder_button = tk.Button(root, text="Selecionar", command=lambda: select_folder(output_folder_label))
output_folder_button.grid(row=5, column=2)

# Botão de Execução
run_button = tk.Button(root, text="Executar Análise", command=run_analysis)
run_button.grid(row=6, column=1, pady=10)

root.mainloop()
