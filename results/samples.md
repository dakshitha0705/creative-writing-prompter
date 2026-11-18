# Sample outputs

Trigram model with backoff, tuned k per genre, seed 42, 20 words each.
Lower temperature = safer, more repetitive; higher = more surprising, less grammatical.

## mystery

**"The detective opened the ..."** - next-word suggestions: door (0.32), case (0.06), window (0.03), salon (0.03), stable (0.03)

- T=0.5: The detective opened the *door. i was off to france. i had been lounging in his hand. i am afraid not very gracious. i*
- T=1.0: The detective opened the *window. he was with his top hat and the moral retrogression which when it was the children say said royce*
- T=1.5: The detective opened the *stable lane. if a rod of six foot society would meekly make up his shiny seedy coat his red curls*

**"It was a dark ..."** - next-word suggestions: lantern (0.06), chin (0.03), figure (0.03), outline (0.03), strong (0.03)

- T=0.5: It was a dark *lantern. i was off to france. i had been lounging in his hand. i am afraid not very gracious. i*
- T=1.0: It was a dark *lantern. he was with his top hat and the moral retrogression which when it was the children say said royce*
- T=1.5: It was a dark *lantern. said he my real name said he i cannot imagine. but are there. that's true he cried and shook*

**"Holmes looked at the ..."** - next-word suggestions: time (0.05), door (0.05), window (0.03), other (0.03), end (0.03)

- T=0.5: Holmes looked at the *sight of the house. and then the first time. i had been so uncommon so complete an alibi i could*
- T=1.0: Holmes looked at the *same as ever. what a surprise it was a very large hints. a double ring but it ends abruptly and*
- T=1.5: Holmes looked at the *abruptness of the company once more upon his brow was all laid before me. her name and what they like*

## horror

**"I heard a sound in the ..."** - next-word suggestions: first (0.02), morning (0.02), rue (0.01), same (0.01), meantime (0.01)

- T=0.5: I heard a sound in the *morning of sunday and who appeared to me that i had been guilty of robbery when you made the attempt*
- T=1.0: I heard a sound in the *bath. but in close juxtaposition to the shelf he had no means original in his face to the contemplation of*
- T=1.5: I heard a sound in the *joint diaries of mr schroeter of lilienthal. come open the lantern fall inside the tree and the inevitable conclusion a*

**"The corpse ..."** - next-word suggestions: of (0.05), was (0.04), to (0.04), and (0.03), being (0.01)

- T=0.5: The corpse *i was not only not far from the greater part of the murder. the first place to bring into light*
- T=1.0: The corpse *with their whole forearms in no one could be done openly. i had it seems likely to interfere with my*
- T=1.5: The corpse *it was just as a kind which enabled him to the shadow of the bandage. they who dream by day*

**"At midnight the ..."** - next-word suggestions: most (0.01), whole (0.01), first (0.01), same (0.01), house (0.01)

- T=0.5: At midnight the *corpse of the room. the studding sail booms and rolling every moment. the wind is still one foot wide was*
- T=1.0: At midnight the *hundred and fifty thousand francs and handed it to the fact that the articles having been printed under the fog*
- T=1.5: At midnight the *courtiers who stood near him. genius claims kindred with the sense of my condenser. they who dream by day more*

## scifi

**"The machine ..."** - next-word suggestions: and (0.05), at (0.05), were (0.05), his (0.05), that (0.00)

- T=0.5: The machine *the little man and he did not answer. it was the pride of her heart. he had not been trained*
- T=1.0: The machine *the last word of this visionary world was very clear in her eyes were unusually deep. was i tell you*
- T=1.5: The machine *the forest. surely it would be fair. no moth was to the tips. elizabeth sat apart blind and these people*

**"We looked up at the stars and ..."** - next-word suggestions: the (0.06), when (0.06), which (0.06), then (0.00), he (0.00)

- T=0.5: We looked up at the stars and *when next it rose over europe everywhere were crowds of watchers on hilly slopes on house roofs in open order*
- T=1.0: We looked up at the stars and *when next his mother to his proposition but responded with another. the air at the cheek. was i tell you*
- T=1.5: We looked up at the stars and *when next his mother he ventured to put men aboard to sit down and level country that the terrestrial crystal*

**"The Martians ..."** - next-word suggestions: if (0.10), who (0.10), a (0.10), do (0.00), were (0.00)

- T=0.5: The Martians *who hopped about the hall table he said. the light of the great circular windows which opened freely gave the*
- T=1.0: The Martians *who hopped about the great eye specialist. he had nothing else of the brunette type and the himalaya were melting*
- T=1.5: The Martians *who hopped about the great managers. and from that following as i must say i could of the earth near*
