# 🚀 Todo AI Chatbot – Phase III (AI + MCP Architecture)

![Python](https://img.shields.io/badge/Python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green) ![OpenAI](https://img.shields.io/badge/OpenAI-Agents-orange) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-blue) ![Architecture](https://img.shields.io/badge/Architecture-Stateless-purple) ![Development](https://img.shields.io/badge/Development-Spec--Driven-yellow)

An AI-powered Todo Chatbot built using an Agentic Development Workflow and Spec-Driven Development approach. This project allows users to manage tasks using natural language through OpenAI Agents and MCP tools in a fully stateless and scalable architecture.

## 🏗 Architecture Overview

Frontend (ChatKit)  
↓  
FastAPI Chat Endpoint  
↓  
OpenAI Agents SDK  
↓  
MCP Server (Task Tools)  
↓  
Neon PostgreSQL

## ✨ Natural Language Examples

Add a task to buy groceries  
Show me all my tasks  
What's pending?  
Mark task 3 as complete  
Delete the meeting task  
Change task 1 to "Call mom tonight"  
What have I completed?

The AI agent intelligently selects and invokes the correct MCP tool based on user intent.

## 📁 Project Structure

/frontend   → ChatKit UI  
/backend    → FastAPI + Agents SDK + MCP  
/specs      → Agent & MCP tool specifications

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | OpenAI ChatKit |
| Backend | Python FastAPI |
| AI Framework | OpenAI Agents SDK |
| Tool Layer | Official MCP SDK |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |

## 🧠 Development Approach

This project was built using:

### ✅ Agentic Development Workflow
Spec → Plan → Break into Tasks → Implement via Claude Code

### ✅ Spec-Driven Development
All system behaviors, MCP tools, API contracts, and agent logic were defined in specification files before implementation.  
This ensured:
- Clear architecture design  
- Predictable behavior  
- Reproducible workflows  
- Structured AI-tool interaction  

No manual coding shortcuts — implementation strictly followed specifications.

## ⚙ Setup Instructions

### Backend Setup
cd backend  
pip install -r requirements.txt  
uvicorn main:app --reload

### Frontend Setup
cd frontend  
npm install  
npm run dev

## 🚀 Deployment

- Frontend → Vercel  
- Backend → Render / Railway  
- Database → Neon PostgreSQL

## 🎯 Learning Outcomes

- Agentic Development Workflow (Spec → Plan → Tasks → Implementation)  
- MCP Tool Architecture  
- Stateless Backend Systems  
- AI-driven Task Automation  
- Scalable Production Architecture  
- Spec-Driven Development Methodology

## 🔮 Future Improvements

- Task priority system  
- Due dates & reminders  
- Advanced filtering  
- Multi-user dashboard  
- Voice-based commands

## 👩‍💻 Author

**Anusha Qasim**  
Frontend Developer | AI Enthusiast  
Hackathon 2 – Phase III

⭐ If you found this project interesting, consider giving it a star!
