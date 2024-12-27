web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker api3:app --bind 0.0.0.0:$PORT
dashboard: streamlit run app3.py --server.port=8501 --server.address=0.0.0.0
