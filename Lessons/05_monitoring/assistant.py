{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "e1f620e0",
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "\n",
    "from dotenv import load_dotenv\n",
    "load_dotenv()\n",
    "\n",
    "sys.path.append(\"../01_agentic_rag\")\n",
    "from ingestion import load_faq_data, build_index\n",
    "from rag_helper import RAGBase\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "996425b2",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "llm-zoomcamp (3.14.5)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
