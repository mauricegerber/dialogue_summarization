## Evaluation of Approaches to Summarize Dialogue Transcripts with Focus on User-friendliness

### Python version and libraries
Python 3.7.3

```
dash==1.19.0
dash-bootstrap-components==0.12.0
dash-core-components==1.15.0
dash-html-components==1.1.2
dash-table==4.11.2
DateTime==4.3
Flask==1.1.2
keybert==0.2.0
nltk==3.5
numpy==1.20.1
pandas==1.2.3
plotly==4.14.3
rake-nltk==1.0.4
reportlab==3.5.67
scikit-learn==0.24.1
textsplit==0.5
word2vec==0.11.1
yake==0.4.8
```

### How to start the web app

The web app is available at https://projects.pascalaigner.ch.

But you can also run it on your local machine.

1. Create a virtual environment with the Python version and libraries listed above. For guidance check the official Python documentation at https://docs.python.org/3/tutorial/venv.html.

2. Download the code from this repository.

3. Open the terminal and navigate to the main directory of the repository with `cd .../summarization`.

4. Navigate to the directory of the `app.py` file with `cd Dash`.

5. Start the app with `python app.py`. It is then accessible via http://127.0.0.1:8050.
