# Official Submission Manual: IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS)

---

## 1. Executive Publication & Financial Verification

| Item | IEEE T-ITS Policy | Value for AURA Submission |
| :--- | :--- | :--- |
| **Journal Impact Factor** | Clarivate Journal Citation Reports | **7.9** (Q1, Top-tier flagship) |
| **Journal CiteScore** | Scopus Elsevier | **15.9** (98th Percentile) |
| **Submission Fee** | IEEE ITSS | **$0.00 (₹0)** |
| **Traditional Publication Fee** | IEEE ITSS Subscription Model | **$0.00 (₹0 - No APC)** |
| **Page Limit (Free)** | IEEE Transactions Regular Paper | **Up to 10 Pages** (No overlength charges) |
| **Submission Portal** | ScholarOne Manuscripts | [https://mc.manuscriptcentral.com/t-its](https://mc.manuscriptcentral.com/t-its) |

> [!IMPORTANT]
> **How to ensure $0.00 (₹0) cost on IEEE ScholarOne:**
> During Step 5 ("Details & Comments") or upon final acceptance, IEEE will ask you to choose between:
> 1. **Open Access ($2,495 USD)**
> 2. **Traditional / Subscription ($0.00 / ₹0)**
>
> **Always select Option 2: Traditional / Subscription Publishing**.
> Under this model, IEEE publishes your paper in IEEE Xplore with zero fees charged to you. You retain the right to self-archive the preprint on Zenodo, TechRxiv, or your institutional repository.

---

## 2. Prepared Files Ready in Your `Downloads` Folder

All necessary files are compiled, verified, and placed in `/home/deepak-r/Downloads/`:

1. **`paper_aura_journal.zip`** (or `paper_aura_ieeeconf.zip`):
   - The complete LaTeX source package using official `IEEEtran.cls`.
   - Upload this to Overleaf and click **Recompile** to produce your final submission `main.pdf`.
2. **`IEEE_TITS_Cover_Letter.docx`**:
   - Official cover letter addressed to the Editor-in-Chief of IEEE Transactions on Intelligent Transportation Systems.
3. **`AURA_Highlights.docx`**:
   - 5 structured takeaway highlights.
4. **`AURA_Declaration_of_Interest_Statement.docx`**:
   - Declaration of zero commercial conflicts of interest and zero external funding.

---

## 3. Step-by-Step ScholarOne Submission Walkthrough

### Step 1: Account Login
1. Navigate to the IEEE T-ITS ScholarOne portal:
   👉 **[https://mc.manuscriptcentral.com/t-its](https://mc.manuscriptcentral.com/t-its)**
2. Log in with your IEEE / ScholarOne credentials (or click **Create An Account** if you do not have one).
3. Under the **Author** tab, click **Start New Submission** $\to$ **Begin Submission**.

---

### Step 2: Step 1 - Type, Title, & Abstract
* **Manuscript Type**: Select **Regular Paper**.
* **Title**:
  ```text
  AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption
  ```
* **Running Head / Short Title**:
  ```text
  AURA: Resilient Urban Traffic Signal Control via Semi-Markov RL
  ```
* **Abstract**:
  ```text
  Urban traffic signal optimization requires simultaneously managing non-stationary civilian demand surges and life-critical emergency vehicle (EV) preemption. While Deep Reinforcement Learning (DRL) demonstrates superior adaptability over classical fixed-time schemes, existing learning-based controllers frequently suffer from action-duration instability, violate standard municipal clearance constraints, and trigger severe post-preemption shockwaves in starved cross-street corridors. In this work, we propose AURA (Adaptive Urban Routing and Actuation), a decentralized traffic control architecture formulated as a Semi-Markov Decision Process (SMDP) with action-duration bounds. AURA optimizes discrete signal phase transitions while modeling continuous-time queue dynamics via Neural Ordinary Differential Equations (NeurODEs), deterministically bounding green allocations between 10 s and 45 s based on queue backlogs, and enforcing mandatory 3-second yellow clearance intervals with duration-dependent discounting γ^τ. To prevent post-preemption gridlock, AURA couples dynamic emergency green-wave routing with an active momentum recovery mechanism that explicitly mitigates secondary cross-arterial congestion shockwaves. Evaluated within the microscopic traffic simulator Eclipse SUMO under realistic rush-hour demand against five established baselines—Traditional Fixed-Time, Demand-Responsive Actuated control, theoretical Max-Pressure (2013), modern SOTA PressLight (ACM KDD 2019), and contemporary EVP-DRL (Transportation Research Part C 2023)—across both high-density corridors over multiple random seeds and an authentic 177-intersection OpenStreetMap network of Midtown Manhattan, AURA achieves superior empirical performance. Microscopic evaluations confirm that AURA eliminates phase flickering, accelerates emergency vehicle clearance, dissipates secondary shockwaves up to 5.6x faster, and cuts vehicular CO2 emissions by up to 11.8%. Crucially, with an ultra-lightweight memory footprint of 18.52 KB and a single-core CPU inference latency of 33.28 µs (30,050 decisions/sec), AURA demonstrates O(1) decentralized complexity, enabling real-time control of an entire 10,000-intersection statewide or metropolitan network on a single commodity laptop utilizing <33.3% of a single CPU core and <20 MB RAM without server-farm infrastructure.
  ```

---

### Step 3: Step 2 - File Upload
Upload the following files:
1. **Main Document**: Upload the compiled PDF (`main.pdf` from Overleaf).
   - *File Designation*: **Main Document**
2. **Cover Letter**: Upload `IEEE_TITS_Cover_Letter.docx`.
   - *File Designation*: **Cover Letter**
3. **Optional Supporting Archive**: Upload `paper_aura_journal.zip`.
   - *File Designation*: **Supplemental Material for Reviewer**

---

### Step 4: Step 3 - Attributes / Keywords & EDICS
Select the following IEEE T-ITS keywords / EDICS:
- `Traffic signal control`
- `Deep reinforcement learning`
- `Semi-Markov Decision Process`
- `Emergency vehicle preemption`
- `Intelligent Transportation Systems`
- `Microscopic traffic simulation`
- `Edge computing`

---

### Step 5: Step 4 - Authors & Institutions
* **Author**: Deepak R.
* **Email**: `24deepakrobo099@dhaanishcollege.in` (and/or `wssedd18@gmail.com`)
* **Institution**: Department of Robotics and Automation Engineering, Dhaanish Ahmed College of Engineering
* **City**: Chennai
* **Country**: India
* **ORCID ID**: (Link your ORCID if available)

---

### Step 6: Step 5 - Details & Comments (CRITICAL FOR ₹0 BUDGET)
1. **Cover Letter Text Box**: Copy and paste the text from `IEEE_TITS_Cover_Letter.txt`.
2. **Prior Publication / Conference Overlap**:
   - Answer: *"No, this manuscript is an original full-length journal contribution that has not been published or submitted elsewhere."*
3. **Funding Information**:
   - Select: *"This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors (Self-funded student research)."*
4. **Publishing Model Choice**:
   - When prompted for **Open Access choice**, select:
     👉 **"Traditional / Subscription Model (No Open Access Fee / $0 APC)"**.
5. **Conflict of Interest**:
   - Answer: *"The author declares no competing financial or personal interests."*

---

### Step 7: Step 6 & 7 - Review & Submit
1. ScholarOne will automatically build the review PDF.
2. Click **View PDF Proof**. Inspect all 9–10 pages:
   - Verify that Figure 1 (Architecture diagram) is crisp and legible.
   - Verify that Table II, Figure 2, Table III, Table IV, Table V, and Figure 3 appear cleanly interleaved with the text.
   - Verify that the author biography is present at the end.
3. Click **Submit**!
4. You will receive an immediate confirmation email with your Manuscript ID (e.g., `T-ITS-26-XXXXX`).

---

## 4. Expected Review Timeline for IEEE T-ITS
- **First Decision (Under Review $\to$ Decision)**: 8 to 12 weeks.
- **Review Outcomes**: Minor Revision, Major Revision, or Accept.
- **Publication**: Published in **IEEE Xplore Digital Library** with Scopus and Web of Science indexing.
