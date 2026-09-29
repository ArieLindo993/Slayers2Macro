import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from item_names import canonical_name,name_evidence
from item_history import ItemHistory,parse_reward

def reading(name,sample='frame-a',confidence=.98):
    box=[[20,20],[220,20],[220,40],[20,40]]
    quantity=[[80,55],[115,55],[115,70],[80,70]]
    result=parse_reward([(box,name,confidence),(quantity,'x1',.98)],width=500)
    result['sample_id']=sample
    return result

class StrictNames(unittest.TestCase):
    def test_reported_variants_merge_without_changing_quantities(self):
        groups={'Golden Fish':['Golden Fish','Goden Fish','Goiden Fish','Gorden Fish'],
                'Clown Fish':['Clown Fish','Cown Fish','clown f'],
                'Coral':['Coral','Conal'],
                'Crustadon':['Crustadon','cstadon','Custadon','ostadon','tadon'],
                'Sea Horse':['Sea Horse','SeaHorse','eaHorse','seHorse']}
        h=ItemHistory();cycle=0
        for expected,variants in groups.items():
            for name in variants:
                h.record(cycle,reading(name));cycle+=1
            self.assertEqual(h.totals()[expected],len(variants))
        self.assertEqual(len(h.totals()),len(groups));self.assertEqual(h.total,cycle)

    def test_fragments_do_not_become_species_or_lose_reward_count(self):
        h=ItemHistory()
        fragments=['Fish','a Fish','n Fish','en Fish','Ore','Scraps','Fwesh','orse']
        for cycle,name in enumerate(fragments):
            h.record(cycle,reading(name))
            h.identify(cycle,reading(name,'frame-b'))
            self.assertFalse(h.by_cycle[cycle]['identified'])
        self.assertEqual(h.totals(),{'Nome não identificado':len(fragments)})

    def test_new_name_requires_two_distinct_images_and_high_confidence(self):
        h=ItemHistory();h.record(0,reading('Silver Compass',confidence=.93))
        h.identify(0,reading('Silver Compass',confidence=.93))
        self.assertFalse(h.by_cycle[0]['identified'])
        h.identify(0,reading('Silver Compass','frame-b',.93))
        self.assertEqual(h.by_cycle[0]['name'],'Silver Compass')
        h.record(1,reading('Other Compass','frame-c',.89))
        h.identify(1,reading('Other Compass','frame-d',.89))
        self.assertFalse(h.by_cycle[1]['identified'])
        h.record(2,reading('Sllver Compass','frame-e'))
        h.identify(2,reading('Sllver Compass','frame-f'))
        self.assertFalse(h.by_cycle[2]['identified'])

    def test_distinct_real_items_are_not_fuzzily_merged(self):
        self.assertNotEqual(canonical_name('OuwFish'),canonical_name('OuwFwesh'))
        self.assertNotEqual(canonical_name('Refinement Ore'),canonical_name('Mythic Refinement Ore'))
        self.assertFalse(name_evidence('Clown Triggerfish')[1])

    def test_later_error_cannot_replace_validated_name(self):
        h=ItemHistory();h.record(0,reading('Golden Fish'))
        h.identify(0,reading('Fish','frame-b'))
        h.identify(0,reading('Clown Fish','frame-c'))
        self.assertEqual(h.by_cycle[0]['name'],'Golden Fish');self.assertEqual(h.total,1)

    def test_repeated_unlisted_typo_is_not_learned_as_new_species(self):
        h=ItemHistory()
        h.record(0,reading('Gloden Fish'))
        h.identify(0,reading('Gloden Fish','frame-b'))
        self.assertFalse(h.by_cycle[0]['identified']);self.assertEqual(h.total,1)

    def test_late_confirmation_preserves_quantity_with_unknown_name(self):
        h=ItemHistory();h.record_outcome(0,'Sem recompensa detectada')
        self.assertTrue(h.identify(0,reading('Fish'),confirm=True))
        self.assertNotIn('status',h.by_cycle[0]);self.assertEqual(h.total,1)
        self.assertFalse(h.by_cycle[0]['identified'])
        h.identify(0,reading('Zebra Fish','frame-b'))
        self.assertEqual(h.totals(),{'Zebra Fish':1})

    def test_border_clipping_and_pending_vote_memory(self):
        result=parse_reward([([[0,20],[130,20],[130,40],[0,40]],'Golden Fish',.99),
                             ([[60,50],[90,50],[90,65],[60,65]],'x1',.99)],width=400)
        self.assertTrue(result['name_ambiguous']);self.assertFalse(result['name_validated'])
        h=ItemHistory()
        for cycle in range(200):h.record(cycle,reading('Silver Compass',str(cycle)))
        self.assertLessEqual(len(h.name_votes),2);self.assertEqual(h.total,200)

if __name__=='__main__':unittest.main()
