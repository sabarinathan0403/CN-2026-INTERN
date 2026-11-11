# KALVIKKAN - AI-Based Student Performance Prediction & Early Intervention System

> **Tagline**: Predict Early. Intervene Smartly. Improve Student Success.  
> **Hackathon Edition**: Built for fast, reliable, polished, and production-ready demonstration.

---

## 📌 Problem Statement
In higher education institutions, struggling students often receive academic help only after mid-semester or final exam scores drop significantly—when it is often too late to recover. 

**KALVIKKAN** solves this problem by continuously monitoring early warning signals (attendance trends, internal assessment decline, assignment completion backlogs, and continuous quiz metrics). The system predicts final academic performance, classifies student risk levels using transparent explainable AI factors, and triggers personalized interventions for faculty, parents, and students.

---

## 🌟 Key Features

1. **Role-Based Demo Access**: Single-click role entry for **Faculty**, **Student**, and **Administrator** with zero setup authentication.
2. **Real Student Database**: Contains all 59 real Tamil Nadu engineering student records (EMIS numbers, Aadhar IDs, email IDs, phone numbers, and academic metrics).
3. **Interactive AI Prediction Simulator**: Real-time slider-based scenario testing with transparent scoring algorithm (`40% Prev Marks + 20% Attendance + 15% Assignments + 15% Assessments + 10% Quizzes`).
4. **Explainable AI Risk Factors**: Dynamically pinpoints why a student is flagged (e.g., *Low Attendance <75%*, *Mathematics Score Decline*, *Incomplete Assignments*).
5. **Early Intervention Workflows**: Start mentor meetings, assign remedial classes, set study plans, and update status in real-time (`Pending` ➔ `In Progress` ➔ `Completed`).
6. **Parent & Guardian SMS/Email Alert Dispatcher**: Automated notice log system for notifying parents of attendance and performance warnings.
7. **Personalized Remedial Study Plan Generator**: Generates 6-day study schedules and practice quiz recommendations.
8. **Peer Mentor Matching**: Automatically pairs high-risk students with top-performing peer mentors (e.g., Rahul Dravid M or Srija S).
9. **Kalvikkan AI Interactive Assistant**: Drawer chatbot providing instant answers on student performance, weak subject analysis, and study advice.
10. **Institutional Analytics**: Responsive Recharts visualizations for cohort trends, risk distribution donut charts, and department comparisons.
11. **Dark & Light Theme**: Built-in appearance toggle with persistent `localStorage` support.
12. **Student Achievement Gallery**: Browse each student's uploaded certificates and other credentials, open or download original files, and upload multiple images at once.

---

## 🛠️ Tech Stack

- **Framework**: Next.js 14 / 15 (App Router, React 18, TypeScript)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React (`lucide-react`)
- **Charts**: Recharts (`recharts`)
- **Persistence**: React State & `localStorage` for app records; IndexedDB for uploaded files
- **Deployment**: Vercel ready (Zero backend configuration required)

> **Storage scope:** This demo stores records and uploaded files in the current browser. Faculty using a different browser or device will not see those files until a shared backend and database are configured.

---

## 🚀 How to Run Locally

### Prerequisites
- Node.js (v18.0.0 or higher)
- npm or yarn

### Steps
```bash
# 1. Install dependencies
npm install

# 2. Run the development server
npm run dev

# 3. Open http://localhost:3000 in your browser
```

---

## 📦 How to Build for Production

```bash
# Run production build
npm run build

# Start production server
npm start
```

---

## ☁️ How to Deploy to Vercel

1. Push your repository to GitHub.
2. Log into [Vercel](https://vercel.com) and click **Import Project**.
3. Select your repository and choose **Next.js** framework preset.
4. Click **Deploy**. No environment variables or custom build scripts are needed!

---

## 🎬 Hackathon Demonstration Flow (3-5 Minutes)

1. **STEP 1 — Landing Page**: Open application at `/`, view hero features, click **[ Continue as Faculty ]**.
2. **STEP 2 — Faculty Dashboard**: Review institutional KPIs (120 total students, 13 high-risk), inspect the **Donut Risk Chart** and **Kalvikkan AI Insight Card**.
3. **STEP 3 — Student Profile**: Click **[ View ]** on a high-risk student (e.g. *ABISHEK S*). Inspect EMIS ID, Aadhar ID, explainable impact factors, and click **[ Remedial Plan ]**.
4. **STEP 4 — AI Prediction Simulator**: Navigate to `/predict`. Adjust sliders for Attendance, Assessment, and Assignments. Click **[ Analyze Student ]** to observe live predicted score, confidence rating, and generated recommendations.
5. **STEP 5 — Early Intervention**: Click **[ Start Intervention ]**, select **Mentor Meeting**, set priority to **High**, and submit. Observe status update to **In Progress**.
6. **STEP 6 — Parent Alert**: Click **[ Parent Alert ]**, preview the automated notification message, and click **[ Dispatch Alert Now ]**.
7. **STEP 7 — Student Demo**: Switch to **Student Demo** role to view personalized recommendations, weak subject highlighting (Mathematics: 56%), and peer mentor matching.
