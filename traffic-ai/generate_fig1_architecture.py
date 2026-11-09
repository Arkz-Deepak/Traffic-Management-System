import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set high-resolution publication styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.weight'] = 'normal'

# Create canvas: 16 inches x 5.2 inches at 300 DPI -> 4800 x 1560 pixels
fig, ax = plt.subplots(figsize=(16, 5.2), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 5.2)
ax.axis('off')

# Background canvas
bg = patches.Rectangle((0, 0), 16, 5.2, facecolor='#FFFFFF', edgecolor='none', zorder=0)
ax.add_patch(bg)

# Palette definition
C_BLUE_BG = '#F0F7FF'
C_BLUE_BORDER = '#2B6CB0'
C_BLUE_TITLE = '#1A365D'

C_VIOLET_BG = '#F5F3FF'
C_VIOLET_BORDER = '#7C3AED'
C_VIOLET_TITLE = '#4C1D95'

C_PURPLE_BG = '#FAF5FF'
C_PURPLE_BORDER = '#805AD5'
C_PURPLE_TITLE = '#44337A'

C_AMBER_BG = '#FFFBEB'
C_AMBER_BORDER = '#D97706'
C_AMBER_TITLE = '#78350F'

C_GREEN_BG = '#ECFDF5'
C_GREEN_BORDER = '#059669'
C_GREEN_TITLE = '#064E3B'

C_RED_BG = '#FEF2F2'
C_RED_BORDER = '#DC2626'
C_RED_TITLE = '#7F1D1D'

def draw_card(ax, x, y, w, h, bg_color, border_color, lw=1.2, radius=0.18):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=bg_color, edgecolor=border_color,
        linewidth=lw, zorder=2
    )
    ax.add_patch(box)
    return box

def draw_badge(ax, x, y, text, bg_color, border_color, text_color='#FFFFFF', fontsize=8, pad=0.15):
    t = ax.text(x, y, text, fontsize=fontsize, fontweight='bold', color=text_color,
                ha='center', va='center', zorder=5,
                bbox=dict(boxstyle=f'round,pad={pad}', facecolor=bg_color, edgecolor=border_color, lw=0.8))
    return t

# =========================================================================
# STAGE 1: LOCALIZED PERCEPTION (x: 0.35 to 3.20, width: 2.85)
# =========================================================================
s1_x, s1_w = 0.35, 2.85
draw_card(ax, s1_x, 0.95, s1_w, 3.95, C_BLUE_BG, C_BLUE_BORDER, lw=1.5)
draw_badge(ax, s1_x + s1_w/2, 4.90, "STAGE 1: LOCALIZED PERCEPTION", C_BLUE_BORDER, C_BLUE_BORDER, fontsize=8.5)

# Sub-card 1a: Approach Queues
draw_card(ax, s1_x + 0.12, 3.55, s1_w - 0.24, 1.15, '#FFFFFF', '#93C5FD', lw=1.0)
ax.text(s1_x + s1_w/2, 4.45, "Approach Queue Vector", fontsize=9, fontweight='bold', color='#1E3A8A', ha='center', va='center', zorder=4)
ax.text(s1_x + s1_w/2, 4.15, r"$\mathbf{q}(t) = [q_l(t)]_{l \in \mathcal{L}_j^{\mathrm{in}}}$", fontsize=8.5, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s1_x + s1_w/2, 3.80, "Real-time halting vehicle counts", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# Sub-card 1b: Signal State & Timer
draw_card(ax, s1_x + 0.12, 2.30, s1_w - 0.24, 1.10, '#FFFFFF', '#93C5FD', lw=1.0)
ax.text(s1_x + s1_w/2, 3.18, "Active Phase & Timer", fontsize=9, fontweight='bold', color='#1E3A8A', ha='center', va='center', zorder=4)
ax.text(s1_x + s1_w/2, 2.88, r"$\phi_j(t) \in \Phi_j, \quad \tau_{\mathrm{elapsed}} \geq 0$", fontsize=8.5, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s1_x + s1_w/2, 2.55, "Current signal index & green time", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# Sub-card 1c: EV Telemetry
draw_card(ax, s1_x + 0.12, 1.05, s1_w - 0.24, 1.10, C_RED_BG, '#FCA5A5', lw=1.0)
ax.text(s1_x + s1_w/2, 1.93, "Emergency Telemetry", fontsize=9, fontweight='bold', color=C_RED_TITLE, ha='center', va='center', zorder=4)
ax.text(s1_x + s1_w/2, 1.63, r"$d_{\mathrm{EV}} \leq 120\,\mathrm{m}, \quad v_{\mathrm{EV}} \approx 20\,\mathrm{m/s}$", fontsize=8.5, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s1_x + s1_w/2, 1.30, "Rolling corridor optical/siren trigger", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# =========================================================================
# STAGE 2: CONTINUOUS DYNAMICS (NeurODEs) (x: 3.55 to 6.40, width: 2.85)
# =========================================================================
s2_x, s2_w = 3.55, 2.85
draw_card(ax, s2_x, 0.95, s2_w, 3.95, C_VIOLET_BG, C_VIOLET_BORDER, lw=1.5)
draw_badge(ax, s2_x + s2_w/2, 4.90, "STAGE 2: CONTINUOUS DYNAMICS", C_VIOLET_BORDER, C_VIOLET_BORDER, fontsize=8.5)

# Sub-card 2a: NeurODE Queue Evolution
draw_card(ax, s2_x + 0.12, 2.95, s2_w - 0.24, 1.75, '#FFFFFF', '#C4B5FD', lw=1.0)
ax.text(s2_x + s2_w/2, 4.45, "Neural ODE Queue Flow", fontsize=9, fontweight='bold', color=C_VIOLET_TITLE, ha='center', va='center', zorder=4)
ax.text(s2_x + s2_w/2, 4.10, r"$\frac{d s_j(t)}{dt} = f_\theta(s_j(t), \phi_j)$", fontsize=9.5, fontweight='bold', color='#4C1D95', ha='center', va='center', zorder=4)
ax.text(s2_x + s2_w/2, 3.65, r"$s(t+\tau) = s(t) + \int_t^{t+\tau} f_\theta \, du$", fontsize=8.5, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s2_x + s2_w/2, 3.25, "Continuous intra-phase queue trajectory", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# Sub-card 2b: Continuous Discounting
draw_card(ax, s2_x + 0.12, 1.05, s2_w - 0.24, 1.75, '#FFFFFF', '#C4B5FD', lw=1.0)
ax.text(s2_x + s2_w/2, 2.55, "Continuous Discounting", fontsize=9, fontweight='bold', color=C_VIOLET_TITLE, ha='center', va='center', zorder=4)
ax.text(s2_x + s2_w/2, 2.20, r"$\gamma^\tau = \exp\left(-\int_0^\tau \alpha \, du\right)$", fontsize=9.5, fontweight='bold', color='#4C1D95', ha='center', va='center', zorder=4)
ax.text(s2_x + s2_w/2, 1.75, r"Continuous SMDP Bellman Discount", fontsize=8, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s2_x + s2_w/2, 1.35, "Duration-dependent value propagation", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# =========================================================================
# STAGE 3: DECENTRALIZED SMDP POLICY (x: 6.75 to 9.60, width: 2.85)
# =========================================================================
s3_x, s3_w = 6.75, 2.85
draw_card(ax, s3_x, 0.95, s3_w, 3.95, C_PURPLE_BG, C_PURPLE_BORDER, lw=1.8)
draw_badge(ax, s3_x + s3_w/2, 4.90, "STAGE 3: DECENTRALIZED SMDP POLICY", C_PURPLE_BORDER, C_PURPLE_BORDER, fontsize=8.5)

# Policy Network Architecture
draw_card(ax, s3_x + 0.12, 2.70, s3_w - 0.24, 2.00, '#FFFFFF', '#D8B4FE', lw=1.0)
ax.text(s3_x + s3_w/2, 4.45, "Ultra-Lightweight 2-Layer MLP", fontsize=9, fontweight='bold', color=C_PURPLE_TITLE, ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 4.10, r"$4 \to 64 \to 64 \to |\Phi_j|$ (ReLU)", fontsize=8.5, fontweight='bold', color='#581C87', ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 3.70, r"$a_j^*(t) = \arg\max_{a \in \Phi_j} Q(s_j, a; \theta)$", fontsize=8.5, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 3.30, r"$\mathcal{L}(\theta) = \mathbb{E}[(y_t - Q(s,a;\theta))^2]$", fontsize=8, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 2.95, r"$y_t = r(s,a) + \gamma^\tau \max_{a'} Q(s',a';\theta^-)$", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# Edge Compute Hardware Badge
draw_card(ax, s3_x + 0.12, 1.05, s3_w - 0.24, 1.50, '#FAF5FF', '#A855F7', lw=1.2)
ax.text(s3_x + s3_w/2, 2.30, "Edge Compute Profile", fontsize=9, fontweight='bold', color=C_PURPLE_TITLE, ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 1.95, r"$\mathbf{4{,}740}$ Params | $\mathbf{18.52\,KB}$ Memory", fontsize=8.5, fontweight='bold', color='#6B21A8', ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 1.62, r"Inference: $\mathbf{33.28\,\mu s}$ (30,050 dec/s/core)", fontsize=8, fontweight='bold', color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s3_x + s3_w/2, 1.30, "10k Intersections on < 33% CPU Core", fontsize=7.5, color='#047857', fontweight='bold', ha='center', va='center', zorder=4)

# =========================================================================
# STAGE 4: SAFETY & MITIGATION (x: 9.95 to 12.80, width: 2.85)
# =========================================================================
s4_x, s4_w = 9.95, 2.85
draw_card(ax, s4_x, 0.95, s4_w, 3.95, C_AMBER_BG, C_AMBER_BORDER, lw=1.5)
draw_badge(ax, s4_x + s4_w/2, 4.90, "STAGE 4: SAFETY & MITIGATION", C_AMBER_BORDER, C_AMBER_BORDER, fontsize=8.5)

# Sub-card 4a: Action-Duration Envelope
draw_card(ax, s4_x + 0.12, 2.95, s4_w - 0.24, 1.75, '#FFFFFF', '#FDE68A', lw=1.0)
ax.text(s4_x + s4_w/2, 4.45, "Action-Duration Envelope", fontsize=9, fontweight='bold', color=C_AMBER_TITLE, ha='center', va='center', zorder=4)
ax.text(s4_x + s4_w/2, 4.10, r"$\tau = \max(10\,\mathrm{s}, \, \min(2 q_{\mathrm{act}}, \, 45\,\mathrm{s}))$", fontsize=8.5, fontweight='bold', color='#92400E', ha='center', va='center', zorder=4)
ax.text(s4_x + s4_w/2, 3.70, r"Clearance: $t_{\mathrm{yellow}} = 3\,\mathrm{s}$ (deterministic)", fontsize=8, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s4_x + s4_w/2, 3.30, "Strict Municipal Clearance Compliance", fontsize=7.5, color='#047857', fontweight='bold', ha='center', va='center', zorder=4)

# Sub-card 4b: Rolling EVP & Momentum Flush
draw_card(ax, s4_x + 0.12, 1.05, s4_w - 0.24, 1.75, C_RED_BG, '#FCA5A5', lw=1.0)
ax.text(s4_x + s4_w/2, 2.55, "Rolling EVP & Momentum Flush", fontsize=9, fontweight='bold', color=C_RED_TITLE, ha='center', va='center', zorder=4)
ax.text(s4_x + s4_w/2, 2.20, r"Green Wave: $a_j \leftarrow \phi_{\mathrm{EV}} \quad (d_{\mathrm{EV}} \leq 120\,\mathrm{m})$", fontsize=8, fontweight='bold', color='#991B1B', ha='center', va='center', zorder=4)
ax.text(s4_x + s4_w/2, 1.75, r"Momentum Flush: $r_{\mathrm{momentum}}(s_j)$", fontsize=8, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s4_x + s4_w/2, 1.35, r"Suppresses Shockwave ($T_{\mathrm{rec}} \downarrow 44.7\%$)", fontsize=7.5, color='#047857', fontweight='bold', ha='center', va='center', zorder=4)

# =========================================================================
# STAGE 5: PHYSICAL EXECUTION (x: 13.15 to 15.65, width: 2.50)
# =========================================================================
s5_x, s5_w = 13.15, 2.50
draw_card(ax, s5_x, 0.95, s5_w, 3.95, C_GREEN_BG, C_GREEN_BORDER, lw=1.5)
draw_badge(ax, s5_x + s5_w/2, 4.90, "STAGE 5: PHYSICAL EXECUTION", C_GREEN_BORDER, C_GREEN_BORDER, fontsize=8.5)

# Sub-card 5a: TraCI Actuator
draw_card(ax, s5_x + 0.12, 2.95, s5_w - 0.24, 1.75, '#FFFFFF', '#A7F3D0', lw=1.0)
ax.text(s5_x + s5_w/2, 4.45, "TraCI Signal Actuator", fontsize=9, fontweight='bold', color=C_GREEN_TITLE, ha='center', va='center', zorder=4)
ax.text(s5_x + s5_w/2, 4.05, "Bounded Actuation", fontsize=8.5, fontweight='bold', color='#065F46', ha='center', va='center', zorder=4)
ax.text(s5_x + s5_w/2, 3.65, r"$(\phi_{\mathrm{target}}, \tau_{\mathrm{green}}, 3\mathrm{s}\,\mathrm{Y})$", fontsize=8, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s5_x + s5_w/2, 3.25, r"$\mathcal{O}(1)$ Local Execution", fontsize=8, color='#047857', fontweight='bold', ha='center', va='center', zorder=4)

# Sub-card 5b: Microscopic SUMO
draw_card(ax, s5_x + 0.12, 1.05, s5_w - 0.24, 1.75, '#FFFFFF', '#A7F3D0', lw=1.0)
ax.text(s5_x + s5_w/2, 2.55, "Microscopic SUMO", fontsize=9, fontweight='bold', color=C_GREEN_TITLE, ha='center', va='center', zorder=4)
ax.text(s5_x + s5_w/2, 2.15, "Krauss Car-Following", fontsize=8, color='#1F2937', ha='center', va='center', zorder=4)
ax.text(s5_x + s5_w/2, 1.75, "Midtown Manhattan OSM", fontsize=8, fontweight='bold', color='#065F46', ha='center', va='center', zorder=4)
ax.text(s5_x + s5_w/2, 1.35, "177 Junctions / 661 Edges", fontsize=7.5, color='#4B5563', ha='center', va='center', zorder=4)

# =========================================================================
# FORWARD CONNECTING ARROWS & BADGES
# =========================================================================
arrow_kw = dict(arrowstyle="-|>", mutation_scale=14, color='#4B5563', lw=1.6, zorder=6)
red_arrow_kw = dict(arrowstyle="-|>", mutation_scale=14, color='#DC2626', lw=1.6, linestyle='--', zorder=6)

# Stage 1 -> Stage 2 (Perception to NeurODEs)
p1 = patches.FancyArrowPatch((s1_x + s1_w, 3.8), (s2_x, 3.8), **arrow_kw)
ax.add_patch(p1)
ax.text((s1_x + s1_w + s2_x)/2, 4.02, r"$s_j(t)$", fontsize=8, fontweight='bold', color='#1E3A8A', ha='center', va='bottom', zorder=7)

# Stage 2 -> Stage 3 (Continuous State to SMDP Agent)
p2 = patches.FancyArrowPatch((s2_x + s2_w, 3.8), (s3_x, 3.8), **arrow_kw)
ax.add_patch(p2)
ax.text((s2_x + s2_w + s3_x)/2, 4.02, r"$s_j, \gamma^\tau$", fontsize=8, fontweight='bold', color='#581C87', ha='center', va='bottom', zorder=7)

# Stage 3 -> Stage 4 (Target Phase to Safety Envelope)
p3 = patches.FancyArrowPatch((s3_x + s3_w, 3.8), (s4_x, 3.8), **arrow_kw)
ax.add_patch(p3)
ax.text((s3_x + s3_w + s4_x)/2, 4.02, r"$a_j^*(t)$", fontsize=8, fontweight='bold', color='#92400E', ha='center', va='bottom', zorder=7)

# Stage 1 EV Telemetry -> Stage 4 Rolling EVP (Emergency Preempt Trigger)
p_ev = patches.FancyArrowPatch((s1_x + s1_w, 1.6), (s4_x, 1.6), **red_arrow_kw)
ax.add_patch(p_ev)
ax.text(6.6, 1.80, r"Rolling EV Trigger ($d_{\mathrm{EV}} \leq 120\,\mathrm{m}$)", fontsize=7.5, fontweight='bold', color='#B91C1C', ha='center', va='bottom', zorder=7,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#FEF2F2', edgecolor='#F87171', lw=0.8))

# Stage 4 Safety Envelope -> Stage 5 TraCI Actuator
p4 = patches.FancyArrowPatch((s4_x + s4_w, 3.8), (s5_x, 3.8), **arrow_kw)
ax.add_patch(p4)
ax.text((s4_x + s4_w + s5_x)/2, 4.02, r"Bounded $(\phi, \tau)$", fontsize=7.5, fontweight='bold', color='#065F46', ha='center', va='bottom', zorder=7)

# Stage 4 EVP Momentum Flush -> Stage 5 SUMO
p4_ev = patches.FancyArrowPatch((s4_x + s4_w, 1.6), (s5_x, 1.6), **arrow_kw)
ax.add_patch(p4_ev)
ax.text((s4_x + s4_w + s5_x)/2, 1.80, r"Flush Phase", fontsize=7.5, fontweight='bold', color='#065F46', ha='center', va='bottom', zorder=7)

# TraCI Actuator to SUMO (Vertical inside Stage 5)
p5 = patches.FancyArrowPatch((s5_x + s5_w/2, 2.95), (s5_x + s5_w/2, 2.80), **arrow_kw)
ax.add_patch(p5)

# =========================================================================
# CLOSED-LOOP FEEDBACK RETURN (SUMO -> State Perception)
# Clean orthogonal routing along bottom
# =========================================================================
fb_color = '#1D4ED8'
ret_x1 = s5_x + s5_w/2
ret_x0 = s1_x + s1_w/2
ret_y_drop = 0.40

# Down from Stage 5, Left to Stage 1, Up to Stage 1 bottom
ax.plot([ret_x1, ret_x1, ret_x0, ret_x0], [0.95, ret_y_drop, ret_y_drop, 0.90],
        color=fb_color, lw=1.8, zorder=6)
# Arrow tip at the end pointing up
ax.annotate('', xy=(ret_x0, 0.95), xytext=(ret_x0, 0.85),
            arrowprops=dict(arrowstyle="-|>", color=fb_color, lw=1.8, mutation_scale=14), zorder=7)

# Feedback Callout Badge along bottom center
ax.text(8.0, ret_y_drop,
        "Closed-Loop Microscopic Trajectory Feedback: Next State " + r"$s_j(t+\tau)$" + ", Elapsed " + r"$\tau$" + ", Continuous Reward " + r"$r(s_j, a_j)$",
        fontsize=8.5, fontweight='bold', color='#1E40AF', ha='center', va='center', zorder=8,
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#EFF6FF', edgecolor='#60A5FA', lw=1.2))

plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)

# Save high-res raster and PDF versions
out_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper", "fig1_architecture.png")
out_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "paper", "fig1_architecture.pdf")

plt.savefig(out_png, dpi=300, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
plt.close()

print(f"✅ Generated pristine Figure 1 at:\n  - {out_png} (300 DPI PNG)\n  - {out_pdf} (Vector PDF)")
