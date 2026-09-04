with open(r'e:\NewSystem\frontend-vue\src\style.css', 'a', encoding='utf-8') as f:
    f.write('''
.btn-premium-coral {
  background: linear-gradient(135deg, #fb735b, #e15b45);
  color: #ffffff;
  font-weight: 600;
  letter-spacing: -0.01em;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(251, 115, 91, 0.25), inset 0 1px 0 rgba(255,255,255,0.3);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-premium-coral:hover:not(:disabled) {
  box-shadow: 0 14px 28px rgba(251, 115, 91, 0.35), inset 0 1px 0 rgba(255,255,255,0.4);
  transform: translateY(-1px);
}
.btn-premium-coral:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
''')
print('CSS appended')
