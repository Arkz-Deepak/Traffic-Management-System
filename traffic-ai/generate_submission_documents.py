import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

SUBMISSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "submission")
DOWNLOADS_DIR = "/home/deepak-r/Downloads"
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. HIGHLIGHTS (Elsevier standard: 3-5 bullets, max 85 chars each)
# -------------------------------------------------------------
doc_h = docx.Document()
p_h_title = doc_h.add_heading("Research Highlights", level=1)
p_h_sub = doc_h.add_paragraph("AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption")
p_h_sub.runs[0].italic = True

bullets = [
    "SMDP formulation with NeurODE continuous queue dynamics and duration discount.",
    "Deterministic action bounds (10-45s) and 3s clearance stop phase flickering.",
    "Active momentum recovery flushes preemption shockwaves 44.7% faster.",
    "Validated on 177-signal Manhattan network cutting queue backlogs by 13.6%.",
    "Ultra-lightweight 18.52 KB policy runs 10,000 intersections on single core."
]

for b in bullets:
    p = doc_h.add_paragraph(b, style='List Bullet')
    print(f"Highlight ({len(b)} chars): {b}")

h_docx = os.path.join(SUBMISSION_DIR, "Highlights.docx")
doc_h.save(h_docx)
doc_h.save(os.path.join(DOWNLOADS_DIR, "AURA_Highlights.docx"))

with open(os.path.join(SUBMISSION_DIR, "Highlights.txt"), "w") as f:
    for b in bullets:
        f.write(f"- {b} ({len(b)} chars)\n")

# -------------------------------------------------------------
# 2. COVER LETTER (Addressed to TR-C / IEEE T-ITS Editor)
# -------------------------------------------------------------
doc_c = docx.Document()
p_date = doc_c.add_paragraph("November 9, 2026\n")

p_ed = doc_c.add_paragraph(
    "To: The Editor-in-Chief\n"
    "Transportation Research Part C: Emerging Technologies\n"
    "Elsevier B.V.\n"
)
p_ed.runs[0].bold = True

p_subj = doc_c.add_paragraph(
    "Subject: Submission of Research Article titled 'AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption'\n"
)
p_subj.runs[0].bold = True

p_body1 = doc_c.add_paragraph(
    "Dear Editor-in-Chief and Esteemed Editorial Board Members,\n\n"
    "I am pleased to submit our original research manuscript titled \"AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption\" for consideration for publication as a regular research article in Transportation Research Part C: Emerging Technologies under the traditional (subscription-based) publishing model.\n\n"
    "Emergency vehicle preemption (EVP) and civilian traffic resilience represent a critical socio-technical dilemma in contemporary municipal intelligent transportation systems (ITS). In recent foundational work published in this journal, Lin et al. (Transportation Research Part C, Vol. 150, 2023, p. 104089) demonstrated the acute vulnerability of civilian cross-arterials to post-preemption secondary congestion shockwaves. However, current reinforcement learning architectures remain constrained by uniform discrete-time step intervals, lack deterministic municipal safety clearance guarantees, and frequently trigger dangerous phase flickering during high-density demand regimes.\n\n"
    "To definitively resolve these challenges, our paper presents AURA (Adaptive Urban Routing and Actuation), a decentralized control framework formulated as a Semi-Markov Decision Process (SMDP) with explicit action-duration bounds. Our primary architectural and empirical contributions are:"
)

contribs = [
    "Mathematical SMDP Formulation with NeurODEs: Models continuous-time queue dynamics between phase switches via Neural Ordinary Differential Equations (NeurODEs) paired with duration-discounted Bellman updates.",
    "Statutory Action-Duration Safety Envelope: Deterministically bounds green phases (10 s <= tau <= 45 s) and enforces mandatory 3-second yellow clearance intervals, eliminating erratic phase flickering and pedestrian hazards.",
    "Shockwave Mitigation & Dynamic Green Wave: Introduces an active momentum flush reward mechanism that dissipates secondary cross-corridor congestion shockwaves 44.7% faster than contemporary EVP-DRL.",
    "Rigorous Microscopic Benchmarking in Eclipse SUMO: Benchmarked across five independent random traffic seeds against five established baselines: Webster Fixed-Time, SCATS Actuated, Max-Pressure (Varaiya 2013), PressLight (ACM KDD 2019), and EVP-DRL (TR-C 2023).",
    "Large-Scale Real-World Validation: Empirically proven on an authentic OpenStreetMap network of Midtown Manhattan (177 signalized junctions, 661 edges, 1,501 circulating vehicles), achieving the lowest peak and average queues while cutting EV transit latency by 65.9%.",
    "O(1) Edge Compute Efficiency: With an ultra-lightweight footprint of 18.52 KB and 33.28 us CPU latency, an entire 10,000-intersection statewide network can be coordinated on less than 33.3% of a single consumer laptop CPU core without server-farm infrastructure."
]

for c in contribs:
    doc_c.add_paragraph(c, style='List Bullet')

p_close = doc_c.add_paragraph(
    "\nThis manuscript has not been published previously and is not under consideration for publication elsewhere. All data and simulation files will be openly accessible to ensure full community reproducibility. The author confirms that there are no financial conflicts of interest.\n\n"
    "Thank you very much for your time and consideration of our work.\n\n"
    "Sincerely,\n\n"
    "Deepak R.\n"
    "Department of Robotics and Automation Engineering\n"
    "Dhaanish Ahmed College of Engineering, Anna University\n"
    "Chennai 601301, Tamil Nadu, India\n"
    "Email: 24deepakrobo099@dhaanishcollege.in / wssedd18@gmail.com\n"
)

c_docx = os.path.join(SUBMISSION_DIR, "Cover_Letter.docx")
doc_c.save(c_docx)
doc_c.save(os.path.join(DOWNLOADS_DIR, "AURA_Cover_Letter.docx"))

# -------------------------------------------------------------
# 3. DECLARATION OF COMPETING INTERESTS & FINANCIAL DISCLOSURE
# -------------------------------------------------------------
doc_d = docx.Document()
doc_d.add_heading("Declaration of Competing Interests and Funding Disclosure", level=1)
doc_d.add_paragraph("Manuscript Title: AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption\n")
doc_d.add_paragraph("Author: Deepak R. (Department of Robotics and Automation Engineering, Dhaanish Ahmed College of Engineering, Chennai, India)\n")

doc_d.add_heading("1. Declaration of Competing Interests", level=2)
doc_d.add_paragraph(
    "The author declares that they have no known competing financial interests or personal relationships "
    "that could have appeared to influence the work reported in this paper."
)

doc_d.add_heading("2. Funding Information", level=2)
doc_d.add_paragraph(
    "This research did not receive any specific grant from funding agencies in the public, commercial, "
    "or not-for-profit sectors. The computational experiments and simulations were self-funded and executed "
    "using open-source tools (Eclipse SUMO, PyTorch, OpenStreetMap) on commodity edge computing hardware."
)

doc_d.add_heading("3. CRediT Author Statement", level=2)
doc_d.add_paragraph(
    "Deepak R.: Conceptualization, Methodology, Software (SUMO TraCI, NeurODEs, SMDP Policy), "
    "Validation, Formal analysis, Investigation, Data Curation, Writing - Original Draft, "
    "Writing - Review & Editing, Visualization, Project administration."
)

d_docx = os.path.join(SUBMISSION_DIR, "Declaration_of_Interest_Statement.docx")
doc_d.save(d_docx)
doc_d.save(os.path.join(DOWNLOADS_DIR, "AURA_Declaration_of_Interest_Statement.docx"))

print(f"✅ Generated all official submission documents in:\n  - {SUBMISSION_DIR}\n  - {DOWNLOADS_DIR}")
