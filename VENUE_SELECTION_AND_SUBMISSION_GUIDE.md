# Target Venue Selection and 100% Free Peer-Reviewed Submission Guide

---

## 1. Executive Strategy: Why Journals Instead of Conferences for ₹0 Budget

| Venue Type | Submission Fee | Publication / APC Fee | Attendance / Registration Fee | Total Out-of-Pocket Cost |
| :--- | :--- | :--- | :--- | :--- |
| **IEEE Conferences** (e.g. ITSC, IV, CDC) | $0 | $0 | **$600 – $950 USD** (₹50,000 – ₹80,000) | **₹50,000+ (MANDATORY)** |
| **Top Hybrid Journals** (Elsevier TR-C, IEEE T-ITS) | **$0 (₹0)** | **$0 (₹0)** *(Subscription Track)* | **$0 (₹0)** *(No travel/attendance)* | **₹0 (100% FREE)** |
| **Diamond Open Access Journals** (TMLR, JAIR) | **$0 (₹0)** | **$0 (₹0)** *(Sponsored)* | **$0 (₹0)** | **₹0 (100% FREE)** |

> [!IMPORTANT]
> **Why conferences are a financial trap when you have 0 rupees:**
> IEEE and ACM conferences **require at least one author to register at the full conference rate** (typically $600 to $900 USD) for the paper to appear in IEEE Xplore. If you do not pay, the paper is withdrawn.
> In contrast, **Top Academic Journals** (Elsevier, IEEE Transactions, Springer) operate under the **Traditional Subscription Model**: the author pays **$0.00 (₹0)** from submission to final publication.

---

## 2. Selected Premier Venues (Ranked by Impact and Fit)

### Rank 1 (Top Recommendation): *Transportation Research Part C: Emerging Technologies* (Elsevier)
* **Impact Factor**: **8.3** | **CiteScore**: **15.2** | **Quartile**: **Q1 (Top 1% in Transportation)**
* **Why it is the ideal venue for AURA**:
  1. Our foundational SOTA benchmark in the paper—**Dynamic EVP-DRL by Lin et al. (2023)**—was published in this exact journal (*Transportation Research Part C: Emerging Technologies*, Vol. 150, p. 104089, 2023).
  2. AURA directly builds upon and solves the very shockwave mitigation dilemma formulated in Lin et al., proving a **44.7% faster recovery** and demonstrating scalability on Midtown Manhattan.
  3. Reviewers for TR-C are global experts in reinforcement learning traffic signal control and emergency preemption.
* **Cost to Author**: **$0.00 / ₹0** (Select **Subscription Model** on Editorial Manager).
* **Submission Portal**: [Elsevier Editorial Manager (TR-C)](https://www.editorialmanager.com/trc/)
* **Account**: You already have an active Elsevier Editorial Manager account from your recent JSS submission (`JSSOFTWARE-S-26-03997`)!

---

### Rank 2: *IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS)*
* **Impact Factor**: **7.9** | **CiteScore**: **15.9** | **Quartile**: **Q1**
* **Why it is a strong alternative**:
  - The flagship journal of the IEEE Intelligent Transportation Systems Society (ITSS).
  - Regular papers up to 10 published pages under the traditional subscription model have **$0 APC**.
* **Template**: `IEEEtran.cls` (Already included in your `paper_aura_journal.zip`).

---

### Rank 3: *Transactions on Machine Learning Research (TMLR)*
* **Platform**: OpenReview / Association for Machine Learning Research
* **Why it is attractive**:
  - **100% Diamond Open Access**: 0 fees for authors and readers.
  - Fast turnaround: typically 60 days to decision.
  - Rolling submissions: submit any day of the year without deadline stress.

---

## 3. What Was Fixed in the Manuscript Layout

1. **Switched to IEEE Transactions Journal Format (`IEEEtran.cls`)**:
   - Replaced the restrictive 6-page conference template (`ieeeconf.cls`), which was forcing text and tables to overflow into 9 fragmented pages.
   - Uses the official double-column journal layout with running headers (`\markboth{...}`) and index keywords.
2. **Eliminated Float Clumping on Page 7**:
   - Separated `Table II` and `Figure 2` across consecutive sections.
   - Moved `Figure 3` to the conclusion of the Midtown Manhattan study.
   - Tables I, III, IV, and V now sit neatly within their corresponding columns rather than piling up.
3. **Pristine Standalone 300 DPI Architecture Diagram (`fig1_architecture.png`)**:
   - Replaced fragile TikZ code with an ultra-high-resolution 5-stage graphic with crisp typography and zero overlapping boxes.
4. **Publication-Grade Smoothed Simulation Plots**:
   - Gaussian-smoothed ($C^\infty$) TraCI trajectories eliminating integer step zig-zags.

---

## 4. Step-by-Step Submission Walkthrough for Elsevier (TR-C)

### Prepared Files in `/home/deepak-r/Downloads/`:
- `paper_aura_journal.zip` (LaTeX source bundle ready for Overleaf or Editorial Manager)
- `AURA_Highlights.docx` (Mandatory: 5 bullets, strictly $\le 85$ characters each)
- `AURA_Cover_Letter.docx` (Addressed to the Editor-in-Chief of TR-C)
- `AURA_Declaration_of_Interest_Statement.docx` (Conflict of interest and funding disclosure)

### Submission Steps:
1. Go to **[Elsevier Editorial Manager (TR-C)](https://www.editorialmanager.com/trc/)** and log in with your existing Elsevier credentials.
2. Click **Submit New Manuscript**.
3. **Article Type**: Select **Research Paper** (or **Full Length Article**).
4. **Attach Files**:
   - File 1: **Manuscript** $\to$ Upload compiled `main.pdf` (from Overleaf) or `paper_aura_journal.zip`.
   - File 2: **Highlights** $\to$ Upload `AURA_Highlights.docx`.
   - File 3: **Cover Letter** $\to$ Upload `AURA_Cover_Letter.docx`.
   - File 4: **Declaration of Competing Interests** $\to$ Upload `AURA_Declaration_of_Interest_Statement.docx`.
5. **Manuscript Data**:
   - **Full Title**: `AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption`
   - **Abstract**: Copy and paste from `Abstract` in `main.tex`.
   - **Keywords**:
     - `Traffic signal control`
     - `Deep reinforcement learning`
     - `Semi-Markov Decision Process (SMDP)`
     - `Neural Ordinary Differential Equations (NeurODEs)`
     - `Emergency vehicle preemption`
     - `Shockwave mitigation`
     - `Microscopic simulation (Eclipse SUMO)`
   - **Author**: Deepak R., Department of Robotics and Automation Engineering, Dhaanish Ahmed College of Engineering, Chennai, India.
6. **Funding Information**:
   - Check the box: **"Funding was not received for this work"** (or self-funded).
7. **Publishing Option (CRITICAL FOR ₹0 COST)**:
   - When asked to choose publishing options, select:
     **"Publish as a subscription article (No Open Access Fee / No APC)"**.
   - Your fee will be **$0.00 (₹0.00)**.
8. **Build and Approve PDF**:
   - Editorial Manager will compile your PDF. Check the proof, click **I Accept**, and submit!
