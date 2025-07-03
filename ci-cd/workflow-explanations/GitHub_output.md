# 🛠️ GitHub Actions Outputfil (`GITHUB_OUTPUT`)

## 📌 Hvad er `GITHUB_OUTPUT`?

`GITHUB_OUTPUT` er en **miljøvariabel**, som GitHub Actions automatisk definerer under et job. Den peger på en **midlertidig fil**, hvor du kan skrive outputværdier, som efterfølgende steps i workflowet kan bruge.

---

## 🧠 Hvorfor bruge det?

Det gør det muligt at:

- 📤 Dele data mellem steps i en workflow  
- 🔁 Dynamisk styre, hvad der skal ske i næste step  
- 🐍 Skrive output fra scripts (f.eks. Python) uden at bruge shell-syntax  

---

## 🧪 Eksempel: Python-script skriver output

```python
import os

with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
    print('models_to_deploy=["model1", "model2"]', file=fh)

```

Dette skriver outputtet models_to_deploy=["model1", "model2"]til outputfilen.

---

🔗 Sådan bruges output i workflow YAML
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout kode
        uses: actions/checkout@v3

      - name: Kør Python-script
        id: mit_step
        run: python mit_script.py
        env:
          GITHUB_OUTPUT: ${{ github.output }}

      - name: Brug output fra tidligere step
        run: echo "Modeller: ${{ steps.mit_step.outputs.models_to_deploy }}"
```
---


🧭 Hvordan virker det?

GitHub Actions sætter GITHUB_OUTPUT til en sti til en midlertidig fil.
Når du skriver name=value til filen, bliver det registreret som output.
Outputtet kan derefter bruges i YAML med ${{ steps.<step-id>.outputs.<name> }}.



