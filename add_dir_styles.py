# -*- coding: utf-8 -*-
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.rfind('</style>')
if idx == -1:
    print("No </style> found")
else:
    new_css = '''
/* ==============================================
   FORM DIRECTORY - Glassmorphism Reskin
   ============================================== */

.dir-glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.50);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.70);
  border-radius: 24px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04), 0 10px 20px -5px rgba(0,0,0,0.04);
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.28s cubic-bezier(0.4, 0, 0.2, 1), background 0.28s;
  min-height: 220px;
}

.dir-glass-card:hover {
  transform: translateY(-5px) scale(1.01);
  background: rgba(255, 255, 255, 0.70);
  border-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 20px 30px -8px rgba(99, 102, 241, 0.12), 0 8px 10px -5px rgba(99, 102, 241, 0.06);
}

@media (min-width: 1024px) {
  .dir-card-wide {
    grid-column: span 2;
  }
}

.dir-blob-tr {
  position: absolute;
  top: 0; right: 0;
  width: 120px; height: 120px;
  border-bottom-left-radius: 100%;
  pointer-events: none;
}

.dir-blob-bl {
  position: absolute;
  bottom: -24px; left: -24px;
  width: 100px; height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.dir-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.dir-more-btn {
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 50%;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: #64748b;
  opacity: 0;
  transition: opacity 0.2s, background 0.2s, color 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.dir-glass-card:hover .dir-more-btn {
  opacity: 1;
}

.dir-more-btn:hover {
  background: white;
  color: #6366f1;
}

.dir-card-title-new {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
  letter-spacing: -0.01em;
  transition: color 0.2s;
}

.dir-glass-card:hover .dir-card-title-new {
  color: #4f46e5;
}

.dir-btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.75);
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  white-space: nowrap;
}

.dir-btn-edit:hover {
  background: white;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

.dir-btn-del-new {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.2s, background 0.2s, border-color 0.2s;
  opacity: 0;
}

.dir-glass-card:hover .dir-btn-del-new {
  opacity: 1;
}

.dir-btn-del-new:hover {
  color: #ef4444;
  background: rgba(254, 226, 226, 0.8);
  border-color: rgba(252, 165, 165, 0.5);
}

.dir-mesh-orb {
  position: absolute;
  border-radius: 50%;
  opacity: 0.45;
  filter: blur(40px);
  pointer-events: none;
}

.dir-orb-1 {
  width: 320px; height: 320px;
  background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
  top: -80px; left: -80px;
  animation: orbDrift1 18s ease-in-out infinite;
}

.dir-orb-2 {
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(139,92,246,0.20) 0%, transparent 70%);
  top: 40%; right: -60px;
  animation: orbDrift2 22s ease-in-out infinite;
}

.dir-orb-3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%);
  bottom: 0; left: 30%;
  animation: orbDrift3 16s ease-in-out infinite;
}

@keyframes orbDrift1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(40px, 30px); }
}
@keyframes orbDrift2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, 20px); }
}
@keyframes orbDrift3 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -25px); }
}
'''
    text = text[:idx] + new_css + '\n' + text[idx:]
    with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
        f.write(text)
    print("CSS added successfully")
