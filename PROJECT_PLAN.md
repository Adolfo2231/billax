📄 Planning – Billax

Billax is an AI-powered personal finance assistant designed to help users take control of their money. This document outlines the planning process behind the MVP — from solo team formation to the final concept selection and future roadmap.

🧑‍💻 Project Setup (Solo)

Although this is a solo project, I've structured it using real product development practices.
All planning, execution, and decision-making have been organized using modern tools and methods.

Role:
Developer & Product Owner

Tools:

Planning & Docs: Notion
Task Tracking: Notion
Dev Environment: Python, Flask, SQL, OpenAI (planned)
🔍 Research & Brainstorming

I began by researching common struggles young adults face with personal finance:

Difficulty tracking debt, payments, and savings
Lack of smart insights into spending habits
Overwhelm when trying to budget or plan ahead
Brainstorming Techniques Used:

Mind Mapping to visualize pain points
SCAMPER to explore creative angles
"How Might I..." questions to frame opportunities
How might I help users avoid running out of money?
How might I explain where their money went this week?
How might I simplify debt and payment tracking?
📊 Idea Evaluation

Each idea was scored across 4 criteria:
Feasibility, Impact, Scalability, User Value

Idea	Feasibility	Impact	Scalability	Value	Score
AI Finance Chatbot	5	5	4	5	19
Calendar Reminders	4	4	5	4	17
Expense Tracker (Basic)	5	3	3	3	14
Risks & Constraints:

Integration complexity (Plaid, Stripe, OpenAI)
Data accuracy & privacy handling
Maintaining a helpful, not overwhelming, UX
💡 MVP Decision

Chosen MVP:

An AI-powered chatbot that helps users track income, expenses, and debts — and gives useful financial answers in natural language.
Problem it Solves:
Lack of awareness, planning, and visibility in personal finances.

Who It's For:
Young adults, students, freelancers, or anyone who lives "paycheck to paycheck."

Core MVP Features:

Smart assistant for questions like:
"What did I spend the most on this week?"
"Do I have enough to pay my bills?"
Account, debt, and spending tracker
Payment alerts
Debt-to-income calculation
🧠 Idea Summary

Idea	Strengths	Weaknesses	Decision
Expense Log	Easy to build	Low value	❌
Calendar Reminders	Useful alerts	Not dynamic	❌
AI Chatbot	Insightful, unique	Higher effort	✅
Outcome:
A strong, differentiated MVP that combines real financial data with meaningful insights — not just numbers.

💳 Future Feature: Stripe Payments

As a next phase, I plan to integrate Stripe for managing payments and subscriptions — with support for:

Apple Pay
Google Pay
Notes:

Stripe.js + PaymentRequest API will be used
Apple Pay requires domain verification
HTTPS will be enforced
Webhooks will handle payment confirmation 