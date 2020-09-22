
CLEAN = *.pyc
CLEAN += *.pyo
CLEAN += *.png
CLEAN += __pycache__
CLEAN += *~
CLEAN += Thumbs.db

clean:
	yes | rm -rf $(CLEAN)

