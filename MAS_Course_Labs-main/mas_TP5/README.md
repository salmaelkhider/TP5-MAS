# 🤖 TP Bonus : Communication Multi-Agents avec SPADE

**Master IPS - M2 | Université Mohamed V**  
**Dr. Douae AHMADOUN**

---

## 📋 Objectif

Implémenter un **système de livraison multi-agents** en utilisant le framework **SPADE** (Smart Python Agent Development Environment).

---

## 🔧 Prérequis

### Installation

```bash
pip install spade
```

### Exécuter le code de test

```bash
python main.py
```

> ✅ Le serveur XMPP est lancé automatiquement (pas besoin de terminal séparé)

---

## 📁 Fichiers

| Fichier | Description |
|---------|-------------|
| `exercices.py` | **À COMPLÉTER** |
| `main.py` | Pour tester |
| `solution.py` | ⚠️ Solution (pour l'enseignant) |

---

## 🚀 Instructions

1. **Forker** et **cloner** le repository
2. **Installer** SPADE : `pip install spade`
3. **Compléter** `exercices.py`
4. **Tester** : `python main.py`
5. **Push** votre solution

---

## 💡 Rappels SPADE

### Structure d'un Agent

```python
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

class MonAgent(Agent):
    class MonBehaviour(OneShotBehaviour):
        async def run(self):
            # Envoyer un message
            msg = Message(to="destinataire@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = "Contenu"
            await self.send(msg)
            
            # Recevoir un message
            reponse = await self.receive(timeout=10)
    
    async def setup(self):
        self.add_behaviour(self.MonBehaviour())
```

### Performatifs FIPA-ACL

| Performatif | Usage |
|-------------|-------|
| `cfp` | Appel d'offres |
| `propose` | Faire une offre |
| `refuse` | Refuser |
| `accept-proposal` | Accepter |
| `reject-proposal` | Rejeter |
| `inform` | Informer |

---

## 🎯 Code à rendre

Vous devez exécuter le code dans `exercices.py`
Veuillez joindre à ce repo un screenshot de votre terminal avec toute la séquence des messages entre

```
============================================================
🚚 SIMULATION SYSTÈME DE LIVRAISON SPADE
============================================================
```
et
```
============================================================
✅ SIMULATION TERMINÉE
============================================================
```
---

Bon courage ! 🚀
