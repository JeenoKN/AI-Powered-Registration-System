import re

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Make sure directory card content has correct flex alignment
text += """
.dir-card-inner {
  padding: 24px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 20px !important;
  height: 100% !important;
}

.dir-card-content {
  display: flex !important;
  align-items: flex-start !important;
  gap: 16px !important;
}

.dir-card-text {
  flex: 1 !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}

.dir-card-title {
  font-size: 15px !important;
  font-weight: 600 !important;
  color: #1e293b !important;
  margin: 0 !important;
  line-height: 1.4 !important;
}

.dir-card-desc {
  font-size: 13px !important;
  color: #64748b !important;
  margin: 0 !important;
  line-height: 1.5 !important;
  display: -webkit-box !important;
  -webkit-line-clamp: 2 !important;
  -webkit-box-orient: vertical !important;
  overflow: hidden !important;
}
"""

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(text)

print('style.css updated for card flex layout.')
