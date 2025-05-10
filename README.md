# ARTN7

---

## Deploy

### Deploy progetto su disco
Per deployare una nuova versione in produzione su un disco esterno:
* Aprire il terminale e posizionarsi all'interno della cartella di progetto (la cartella corrente).
* Lanciare lo script `deploy.py` con parametro la cartella di produzione, per esempio:
```angular2html
python3 deploy.py /media/user/DEVICE/ArtN7/
```

### Requirements
Inserire tutte le librerie utilizzate nel file `requirements.txt`. Per ricavarsi automaticamente
tutte le librerie utilizzate si può eseguire il comando puntando all'ambiente di _venv_:
```angular2html
pip freeze > requirements.txt
```

## Pulizia database
Per eliminare i dati delle tabelle del database (senza eliminare il database) eseguire lo script `delete_all.sql`.
