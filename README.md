# FactSearch — Enhanced Fact-Checking Framework

## Overview
FactSearch is a research-oriented fact-checking system built as an extension of the original FacTool framework.  
Its primary goal is to automatically verify factual claims using web search results, natural language inference, and translation, providing structured evidence for each claim.

The project integrates **SearXNG** for backend web search to reduce reliance on external APIs and leverages modern NLP models for claim verification.

---

## Features
- **Parallelised web searches** using SearxNG.
- **Natural Language Inference** for fact-checking claims against retrieved snippets.
- **Structured snippet outputs**: Each result includes content and source URL.
- **Flexible input interface**: Accepts single or paired queries.
- **Extensible architecture**: Designed for future improvements or reintegration with legacy FacTool components.

---

## Installation