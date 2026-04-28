# TERA AI

Assistente desktop para Windows, criado em Python com interface estilizada em CSS (Qt Stylesheet), inspirado no conceito de assistente técnico para profissionais de:

- Programação
- Hardware
- Mobile
- iOS
- Informática

## Funcionalidades atuais

- Cadastro e gestão de tarefas técnicas por área
- Registro de aprendizados (memória de conhecimento)
- Execução de comandos úteis (dev/hardware/mobile) com log salvo
- Persistência completa em banco SQLite
- Exportação do banco de dados
- Sincronização GitHub via menu interno

## Tecnologias

- Python 3
- PySide6 (GUI)
- Qt Stylesheet (CSS)
- SQLite
- PyInstaller (geração de executável)

## Fonte Angels (Dafont)

O projeto está preparado para usar a fonte **Angels**.

1. Baixe a fonte no Dafont
2. Coloque `Angels.ttf` em `assets/fonts/Angels.ttf`

Sem o arquivo, o app usa fallback de fonte automaticamente.

## Como rodar

```bash
python -m pip install -r requirements.txt
python main.py
```

## Gerar executável (.exe)

No Windows:

```bat
build_exe.bat
```

Ao final, o executável fica em:

`dist\Tera\Tera.exe`
