"""
Seed script for PlacementPilot AI.
Populates companies, DSA topics, CS subjects, and interview experiences into DB + ChromaDB.

Usage (from backend/ directory):
    python -m scripts.seed_data
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models.company import Company
from app.models.dsa import DSATopic
from app.services.rag_service import rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DSA_TOPICS = [
    {"name": "Arrays", "description": "Array manipulation, two pointers, sliding window", "category": "Fundamentals", "total_problems": 50},
    {"name": "Strings", "description": "String algorithms, pattern matching, parsing", "category": "Fundamentals", "total_problems": 40},
    {"name": "Linked Lists", "description": "Singly/doubly linked lists, fast-slow pointers", "category": "Data Structures", "total_problems": 30},
    {"name": "Stacks & Queues", "description": "Stack/queue applications, monotonic stack", "category": "Data Structures", "total_problems": 25},
    {"name": "Trees", "description": "Binary trees, BST, tree traversals", "category": "Data Structures", "total_problems": 45},
    {"name": "Graphs", "description": "BFS, DFS, shortest path, topological sort", "category": "Advanced", "total_problems": 40},
    {"name": "Dynamic Programming", "description": "Memoization, tabulation, classic DP patterns", "category": "Advanced", "total_problems": 50},
    {"name": "Greedy", "description": "Greedy algorithms and proofs", "category": "Advanced", "total_problems": 25},
    {"name": "Binary Search", "description": "Binary search on arrays and answer space", "category": "Fundamentals", "total_problems": 30},
    {"name": "Heaps", "description": "Priority queues, heap operations", "category": "Data Structures", "total_problems": 20},
]

COMPANIES = [
    {
        "name": "Google",
        "description": "Global technology leader focusing on search, cloud, and AI products.",
        "difficulty_level": "hard",
        "hiring_process": "Online Assessment -> 4-5 Technical Rounds -> Googleyness Round -> HR",
    },
    {
        "name": "Microsoft",
        "description": "Enterprise software, cloud (Azure), and productivity tools.",
        "difficulty_level": "hard",
        "hiring_process": "Online Coding Test -> 3-4 Technical Interviews -> AA (As Appropriate) Round",
    },
    {
        "name": "Amazon",
        "description": "E-commerce, AWS cloud services, and logistics technology.",
        "difficulty_level": "hard",
        "hiring_process": "Online Assessment -> 4-5 Loop Interviews (LP + Technical) -> Bar Raiser",
    },
    {
        "name": "TCS",
        "description": "India's largest IT services company with global presence.",
        "difficulty_level": "easy",
        "hiring_process": "Aptitude Test (NQT) -> Technical Interview -> HR/MR Round",
    },
    {
        "name": "Infosys",
        "description": "Global consulting and IT services company.",
        "difficulty_level": "easy",
        "hiring_process": "Online Test -> Technical Interview -> HR Round",
    },
    {
        "name": "Wipro",
        "description": "IT, consulting and business process services.",
        "difficulty_level": "easy",
        "hiring_process": "Online Assessment -> Technical + HR Interview",
    },
    {
        "name": "Flipkart",
        "description": "India's leading e-commerce marketplace.",
        "difficulty_level": "medium",
        "hiring_process": "Online Coding Test -> 3 Technical Rounds -> Hiring Manager Round",
    },
    {
        "name": "Razorpay",
        "description": "Indian fintech company providing payment solutions.",
        "difficulty_level": "medium",
        "hiring_process": "Take-home Assignment -> 3 Technical Rounds -> Culture Fit",
    },
    {
        "name": "Goldman Sachs",
        "description": "Global investment banking and financial services.",
        "difficulty_level": "hard",
        "hiring_process": "HackerRank Test -> 3-4 Technical Rounds -> Superday",
    },
    {
        "name": "Adobe",
        "description": "Creative software, digital media, and marketing solutions.",
        "difficulty_level": "medium",
        "hiring_process": "Online Test -> 3 Technical Rounds -> Director Round",
    },
    {
        "name": "Atlassian",
        "description": "Collaboration software including Jira, Confluence, and Bitbucket.",
        "difficulty_level": "hard",
        "hiring_process": "Online Coding Test -> 3-4 Technical Rounds -> Values Interview",
    },
]

INTERVIEW_EXPERIENCES = [
    {
        "company": "Google",
        "role": "Software Engineer",
        "outcome": "selected",
        "difficulty": "hard",
        "experience": """Round 1 - Online Assessment: 2 coding problems in 60 minutes. First was a medium graph problem 
using BFS. Second was a hard DP problem on string partitioning. Passed with good time complexity.

Round 2 - Technical (45 min): Interviewer asked about a system design for a URL shortener at small scale, 
then a coding question on finding k closest points. Focused on clean code and edge cases.

Round 3 - Technical (45 min): Tree-based problem - serialize and deserialize a binary tree. 
Follow-up on optimizing space complexity. Also asked about process vs thread differences.

Round 4 - Googleyness (45 min): Behavioral questions about handling conflict, mentoring juniors, 
and a situation where you had to make a tough technical decision.

Round 5 - Technical (45 min): Hard graph problem - minimum cost to connect all nodes. 
Used Union-Find with Kruskal's algorithm. Interviewer was very collaborative.

Tips: Practice LeetCode medium/hard consistently. Know your projects deeply. 
Google values clear communication during coding.""",
    },
    {
        "company": "Amazon",
        "role": "SDE-1",
        "outcome": "selected",
        "difficulty": "hard",
        "experience": """Online Assessment: 2 coding questions + work style survey + debugging section.
Coding: One array manipulation (two pointers) and one BFS on a grid.

Loop Round 1 (1 hour): Leadership Principles heavy. "Tell me about a time you disagreed with your manager."
Then coding: LRU Cache implementation. Interviewer probed on thread safety.

Loop Round 2 (1 hour): LP question on ownership. Coding: Merge K sorted linked lists using min-heap.
Asked about time/space complexity trade-offs.

Loop Round 3 (1 hour): System design lite - design a notification system. 
Then coding: Word break problem using DP.

Bar Raiser Round (1 hour): Deep LP questions. "Dive deep" into a project from resume.
Coding: Binary tree vertical order traversal.

Key advice: Prepare 8-10 STAR format stories for Leadership Principles. 
Amazon cares more about LP than pure coding skills sometimes.""",
    },
    {
        "company": "TCS",
        "role": "Assistant System Engineer",
        "outcome": "selected",
        "difficulty": "easy",
        "experience": """NQT (National Qualifier Test): Aptitude (quant, reasoning, verbal) + basic coding MCQs.
Coding section had simple C/Java output prediction questions.

Technical Interview (30 min): Questions on OOP concepts - inheritance, polymorphism, abstraction.
Asked to explain my final year project. Simple coding: reverse a string, find factorial.
DBMS: What is normalization? Explain 1NF, 2NF, 3NF with examples.
OS: Difference between process and thread, what is deadlock?

Managerial Round (15 min): Why TCS? Willing to relocate? Family background. 
Very straightforward, no technical grilling.

HR Round (10 min): Salary discussion, joining date, document verification.

Tips: Focus on CS fundamentals (OS, DBMS, OOP). Be confident about your project. 
TCS interviews are generally friendly and not very deep technically.""",
    },
    {
        "company": "Flipkart",
        "role": "Software Development Engineer",
        "outcome": "rejected",
        "difficulty": "medium",
        "experience": """Online Test: 3 coding problems in 90 minutes on HackerRank.
Problems: 1 easy (array sum), 1 medium (binary search variant), 1 hard (graph shortest path).

Round 1 - DSA (60 min): Two sum variant with constraints. Interviewer asked for multiple approaches.
Started with brute force O(n^2), then hash map O(n). Follow-up: what if array is sorted? Two pointers.

Round 2 - DSA + Design (60 min): Design a rate limiter for API endpoints. 
Then coding: longest increasing subsequence. Could only solve O(n^2) DP, struggled with O(n log n).

Round 3 - Hiring Manager (45 min): Deep dive into resume projects. 
Asked about handling production bugs, monitoring, and deployment experience.
Rejected - feedback was insufficient system design knowledge and slow coding on hard problems.

Tips: Flipkart expects strong DSA (medium-hard level) and some system design awareness. 
Practice timed coding regularly.""",
    },
    {
        "company": "Microsoft",
        "role": "Software Engineer",
        "outcome": "selected",
        "difficulty": "hard",
        "experience": """Online Coding (90 min): 2 problems. First: string manipulation with sliding window.
Second: tree traversal with specific ordering requirements.

Round 1 (45 min): Coding - find all anagrams in a string. Clean, bug-free implementation expected.
Discussion on hash map vs array for character counting.

Round 2 (45 min): Coding - lowest common ancestor in a binary tree. 
Then OS questions: virtual memory, paging, page replacement algorithms.

Round 3 (45 min): Coding - design and implement a trie for autocomplete. 
Follow-up: how to handle millions of queries? Discussed caching and sharding at high level.

AA Round (As Appropriate, 30 min): Cultural fit, career goals, why Microsoft.
Discussed work-life balance and team dynamics.

Tips: Microsoft focuses on clean coding and fundamentals. 
Don't rush - talk through your approach before coding. OS and DBMS questions are common.""",
    },
    {
        "company": "Infosys",
        "role": "Systems Engineer",
        "outcome": "selected",
        "difficulty": "easy",
        "experience": """Online Test (InfyTQ): Python/Java programming, DBMS, aptitude.
Programming section: write functions for basic operations, SQL queries.

Technical Interview (25 min): Explain 4 pillars of OOP with real examples.
What is the difference between stack and heap memory?
Write a program to check if a number is prime. Asked to optimize.
SQL: Write a query to find second highest salary from employee table.

HR Interview (15 min): Tell me about yourself. Strengths and weaknesses.
Why Infosys over other companies? Expected CTC discussion.

Overall a relaxed process. Interviewer was helpful when I got stuck on SQL query.
Tips: Know basic SQL, OOP, and be ready to write simple programs on paper/shared editor.""",
    },
    {
        "company": "Razorpay",
        "role": "Backend Engineer",
        "outcome": "selected",
        "difficulty": "medium",
        "experience": """Take-home Assignment (48 hours): Build a REST API for expense splitting (like Splitwise lite).
Required: user auth, add expenses, settle balances. Evaluated on code quality, API design, tests.

Round 1 - Code Review (60 min): Walk through take-home assignment. 
Interviewer asked why I chose certain design patterns, how I'd scale to 1M users.
Questions on database indexing and transaction isolation levels.

Round 2 - DSA (45 min): Implement a thread-safe rate limiter. 
Then: given a stream of transactions, detect fraudulent patterns.

Round 3 - Culture Fit (30 min): Discussion about fintech domain knowledge.
Why Razorpay? Experience with payment systems? How do you handle production incidents?

Tips: Take-home assignments matter a lot. Write clean, tested code with good README. 
Know your assignment inside-out before the interview.""",
    },
]


async def seed_dsa_topics(session) -> None:
    for topic_data in DSA_TOPICS:
        existing = await session.execute(select(DSATopic).where(DSATopic.name == topic_data["name"]))
        if existing.scalar_one_or_none():
            logger.info("DSA topic '%s' already exists, skipping", topic_data["name"])
            continue
        session.add(DSATopic(**topic_data))
        logger.info("Added DSA topic: %s", topic_data["name"])


async def seed_companies(session) -> None:
    for company_data in COMPANIES:
        existing = await session.execute(select(Company).where(Company.name == company_data["name"]))
        if existing.scalar_one_or_none():
            logger.info("Company '%s' already exists, skipping", company_data["name"])
            continue
        session.add(Company(**company_data))
        logger.info("Added company: %s", company_data["name"])


async def seed_interview_experiences() -> None:
    for exp in INTERVIEW_EXPERIENCES:
        doc_id = await rag_service.ingest_experience(
            company=exp["company"],
            role=exp["role"],
            experience=exp["experience"],
            outcome=exp["outcome"],
            difficulty=exp["difficulty"],
        )
        logger.info("Ingested interview experience for %s (%s) -> %s", exp["company"], exp["role"], doc_id)


async def main() -> None:
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_dsa_topics(session)
        await seed_companies(session)
        await session.commit()

    logger.info("Seeding ChromaDB interview experiences...")
    await seed_interview_experiences()

    logger.info("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())