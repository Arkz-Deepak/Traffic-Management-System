import os
import docx
from docx.shared import Pt, Inches, RGBColor

SUBMISSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "submission")
DOWNLOADS_DIR = "/home/deepak-r/Downloads"

doc_tits = docx.Document()

# Date
p_date = doc_tits.add_paragraph("November 9, 2026\n")

# Header
p_ed = doc_tits.add_paragraph(
    "To: The Editor-in-Chief\n"
    "IEEE Transactions on Intelligent Transportation Systems\n"
    "IEEE Intelligent Transportation Systems Society (ITSS)\n"
)
p_ed.runs[0].bold = True

# Subject
p_subj = doc_tits.add_paragraph(
    "Subject: Submission of Original Research Manuscript titled 'AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption'\n"
)
p_subj.runs[0].bold = True

# Salutation & Body
p_body = doc_tits.add_paragraph(
    "Dear Editor-in-Chief and Esteemed Editorial Board Members,\n\n"
    "I am pleased to submit our original research manuscript titled \"AURA: Resilient Urban Traffic Signal Control via Semi-Markov Reinforcement Learning with Action-Duration Bounds and Shockwave-Mitigated Preemption\" for consideration for publication as a Regular Paper in the IEEE Transactions on Intelligent Transportation Systems (IEEE T-ITS) under the Traditional (Subscription) Publishing Track.\n\n"
    "Urban traffic signal control and emergency vehicle preemption (EVP) represent foundational challenges in modern intelligent transportation infrastructure. While deep reinforcement learning (DRL) offers high theoretical adaptability, deploying unconstrained learning controllers directly to municipal road intersections induces severe vulnerabilities: action-duration flickering, violations of statutory yellow clearance constraints, and acute post-preemption secondary congestion shockwaves in starved civilian corridors.\n\n"
    "In this paper, we propose AURA (Adaptive Urban Routing and Actuation), a decentralized control architecture formulated as a Semi-Markov Decision Process (SMDP) with action-duration bounds. The key technical contributions of our work are:\n"
)

bullets = [
    "Semi-Markov Decision Process (SMDP) with NeurODEs: We parameterize continuous-time inter-decision queue dynamics via Neural Ordinary Differential Equations (NeurODEs) paired with duration-dependent Bellman discounting, eliminating arbitrary discrete time-step discretization.",
    "Deterministic Safety Envelopes: We enforce statutory minimum green bounds (10 s <= tau <= 45 s) and mandatory 3-second yellow clearance intervals, eliminating dangerous phase flickering and rear-end collision hazards.",
    "Active Momentum Shockwave Recovery: We formulate a rolling emergency green wave coupled with an active momentum reward that accelerates secondary cross-arterial shockwave dissipation by 44.7% compared to contemporary EVP-DRL.",
    "Multi-Seed Krauss Microscopic Benchmarking in Eclipse SUMO: Rigorously evaluated against five established baselines: Webster Fixed-Time, SCATS Actuated, Max-Pressure (Varaiya 2013), PressLight (ACM KDD 2019), and contemporary EVP-DRL (TR-C 2023) across multiple independent random traffic seeds.",
    "Topological Generalization on Midtown Manhattan OpenStreetMap: Authentically validated on a 177-intersection, 661-edge road network of Midtown Manhattan under 1,501 circulating vehicles, achieving the lowest average and peak network queues while cutting emergency vehicle transit latency by 65.9%.",
    "O(1) Decentralized Edge Complexity: Requiring only 18.52 KB parameter memory and 33.28 us CPU latency per decision (30,050 decisions/sec/core), proving that an entire 10,000-intersection statewide or metropolitan network can be coordinated on less than 33.3% of a single commodity laptop CPU core without server clusters."
]

for b in bullets:
    doc_tits.add_paragraph(b, style='List Bullet')

p_close = doc_tits.add_paragraph(
    "\nIn accordance with IEEE publishing standards, the author confirms that:\n"
    "1. This manuscript is an original work that has not been published previously and is not under consideration for publication elsewhere.\n"
    "2. The author selects the Traditional / Subscription Publishing Model (No Open Access Fee / $0 APC).\n"
    "3. All experimental simulation scripts, neural checkpoints, and OpenStreetMap network configurations are fully open-sourced for complete scientific reproducibility.\n"
    "4. There are no competing financial interests or commercial conflicts associated with this research.\n\n"
    "Suggested Technical Subject Areas / EDICS:\n"
    "• ITS-ATMS: Advanced Traffic Management Systems & Signal Control\n"
    "• ITS-AI: Artificial Intelligence, Reinforcement Learning & Machine Learning in Transportation\n"
    "• ITS-EVP: Emergency Vehicle Priority & Resilient Transit Operations\n"
    "• ITS-SIM: Microscopic Traffic Simulation & Network Modeling\n\n"
    "Thank you very much for your time and editorial evaluation.\n\n"
    "Sincerely,\n\n"
    "Deepak R.\n"
    "Department of Robotics and Automation Engineering\n"
    "Dhaanish Ahmed College of Engineering, Anna University\n"
    "Chennai 601301, Tamil Nadu, India\n"
    "Email: 24deepakrobo099@dhaanishcollege.in / wssedd18@gmail.com\n"
)

out_path = os.path.join(SUBMISSION_DIR, "IEEE_TITS_Cover_Letter.docx")
doc_tits.save(out_path)
doc_tits.save(os.path.join(DOWNLOADS_DIR, "IEEE_TITS_Cover_Letter.docx"))

with open(os.path.join(SUBMISSION_DIR, "IEEE_TITS_Cover_Letter.txt"), "w") as f:
    f.write(p_subj.text + "\n" + p_body.text + "\n")
    for b in bullets:
        f.write(f"- {b}\n")
    f.write(p_close.text)

print(f"✅ Generated IEEE T-ITS Cover Letter at:\n  - {out_path}\n  - {os.path.join(DOWNLOADS_DIR, 'IEEE_TITS_Cover_Letter.docx')}")
