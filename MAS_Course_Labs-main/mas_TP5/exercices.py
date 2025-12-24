import asyncio
import random

# =============================================================================
# INFRASTRUCTURE DE SIMULATION (Remplaçant SPADE)
# =============================================================================

ANNUAIRE = {}

class Message:
    def __init__(self, to, sender=None, body="", performative=""):
        self.to = to
        self.sender = sender
        self.body = body
        self.performative = performative

    def make_reply(self):
        return Message(to=self.sender, performative=self.performative)

class AgentSimule:
    def __init__(self, jid):
        self.jid = jid
        self.mailbox = asyncio.Queue() # Boîte aux lettres
        ANNUAIRE[jid] = self
        self.running = True

    async def send(self, msg):
        msg.sender = self.jid
        if msg.to in ANNUAIRE:
            # On met le message dans la boîte aux lettres du destinataire
            await ANNUAIRE[msg.to].mailbox.put(msg)
        else:
            print(f"⚠️ Erreur: Destinataire {msg.to} inconnu.")

    async def receive(self, timeout=None):
        try:
            if timeout:
                return await asyncio.wait_for(self.mailbox.get(), timeout)
            else:
                return await self.mailbox.get()
        except asyncio.TimeoutError:
            return None

    async def start(self):
        # Méthode à surcharger par les agents spécifiques
        pass

    async def stop(self):
        self.running = False


# =============================================================================
# LOGIQUE MÉTIER (Celle du TP)
# =============================================================================

class LivreurAgent(AgentSimule):
    def __init__(self, jid, tarif, position, disponible=True):
        super().__init__(jid)
        self.tarif = tarif
        self.position = position
        self.disponible = disponible

    def calculer_distance(self, destination):
        return abs(self.position[0] - destination[0]) + abs(self.position[1] - destination[1])

    async def start(self):
        print(f"🚚 {self.jid} prêt (Tarif: {self.tarif}, Pos: {self.position})")
        while self.running:
            # Attendre un message (CFP)
            msg = await self.receive(timeout=1)
            
            if msg:
                if msg.performative == "cfp":
                    # Extraction destination "livraison:(3,4)"
                    try:
                        coords = msg.body.split(":")[1].strip("()").split(",")
                        dest = (int(coords[0]), int(coords[1]))
                        
                        reply = msg.make_reply()
                        
                        if self.disponible:
                            dist = self.calculer_distance(dest)
                            cout = dist * self.tarif
                            reply.performative = "propose"
                            reply.body = f"cout:{cout}"
                            print(f"   -> 🚚 {self.jid} propose {cout} (dist={dist})")
                        else:
                            reply.performative = "refuse"
                            reply.body = "Indisponible"
                            print(f"   -> 🚚 {self.jid} refuse (indisponible)")
                        
                        await self.send(reply)
                    except:
                        pass

                elif msg.performative == "accept-proposal":
                    print(f"🎉 {self.jid}: Livraison ACCEPTÉE! En route...")
                    await asyncio.sleep(1) # Simulation travail
                    
                    confirm = msg.make_reply()
                    confirm.performative = "inform"
                    confirm.body = "done"
                    await self.send(confirm)

                elif msg.performative == "reject-proposal":
                    print(f"😞 {self.jid}: Offre rejetée.")


class GestionnaireAgent(AgentSimule):
    def __init__(self, jid, livreurs_jids):
        super().__init__(jid)
        self.livreurs_jids = livreurs_jids
        self.propositions = []

    async def lancer_livraison(self, destination):
        print(f"\n📢 GESTIONNAIRE: Appel d'offres pour {destination}")
        self.propositions = []

        # 1. Envoyer CFP
        for livreur in self.livreurs_jids:
            msg = Message(to=livreur, performative="cfp", body=f"livraison:{destination}")
            await self.send(msg)

        # 2. Attendre les réponses (pendant 2 secondes)
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < 2:
            msg = await self.receive(timeout=0.5)
            if msg:
                if msg.performative == "propose":
                    cout = float(msg.body.split(":")[1])
                    self.propositions.append({'livreur': msg.sender, 'cout': cout})
                    print(f"   📥 Offre reçue de {msg.sender}: {cout}")
                elif msg.performative == "refuse":
                    print(f"   ❌ {msg.sender} refuse")
        
        # 3. Sélectionner le meilleur
        print(f"\n🔍 Évaluation des {len(self.propositions)} propositions...")
        if not self.propositions:
            print("Aucune offre valide.")
            return

        meilleure = min(self.propositions, key=lambda x: x['cout'])
        gagnant = meilleure['livreur']
        print(f"🏆 LE GAGNANT EST: {gagnant} avec {meilleure['cout']}")

        # 4. Notifier les résultats
        for prop in self.propositions:
            msg = Message(to=prop['livreur'])
            if prop['livreur'] == gagnant:
                msg.performative = "accept-proposal"
            else:
                msg.performative = "reject-proposal"
            await self.send(msg)

        # 5. Attendre confirmation finale
        while True:
            msg = await self.receive(timeout=2)
            if msg and msg.performative == "inform" and msg.body == "done":
                print(f"✅ TRANSACTION TERMINÉE avec {msg.sender}")
                break
            if not msg:
                break

# =============================================================================
# MAIN
# =============================================================================

async def main():
    print("--- SIMULATION SANS SPADE (ASYNCIO PUR) ---")

    # 1. Création des agents
    l1 = LivreurAgent("livreur_A", tarif=2.0, position=(0,0))
    l2 = LivreurAgent("livreur_B", tarif=1.5, position=(5,5)) # Plus proche de (3,4)
    l3 = LivreurAgent("livreur_C", tarif=1.0, position=(10,0), disponible=False)
    
    gest = GestionnaireAgent("gestionnaire", ["livreur_A", "livreur_B", "livreur_C"])

    # 2. Lancement des tâches de fond (les boucles d'écoute des livreurs)
    tasks = [
        asyncio.create_task(l1.start()),
        asyncio.create_task(l2.start()),
        asyncio.create_task(l3.start())
    ]

    # 3. Lancer le scénario du gestionnaire
    await asyncio.sleep(1)
    await gest.lancer_livraison((3, 4))

    # 4. Arrêt
    for agent in [l1, l2, l3]:
        await agent.stop()
    
    # Annuler les tâches en cours proprement
    for t in tasks: t.cancel()
    print("\n--- Fin de simulation ---")

if __name__ == "__main__":
    asyncio.run(main())