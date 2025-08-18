# Trivia Game Demo

This document shows what the trivia game interactions would look like in Discord.

## Starting a Trivia Session

**User:** `!trivia`

**Bot:**
```
**Trivia Game Commands:**
`!trivia start` - Start a new trivia session
`!trivia stop` - Stop the current trivia session
`!trivia next` - Get the next question
`!trivia answer <your_answer>` - Answer the current question
`!trivia scores` - Show current scores
`!trivia add <question> | <answer> [| category]` - Add a new question
`!trivia list [category]` - List available questions

*Tip: Consider using a temporary channel for trivia to keep answers private!*
```

---

**User:** `!trivia start`

**Bot:**
```
💡 Tip: Use a Temporary Channel
For the best trivia experience, consider creating a temporary channel or thread 
so that answers aren't searchable later. You can create a thread by right-clicking 
this message and selecting 'Create Thread'.

Trivia session created! Use `!trivia next` to start the first question.
```

---

## Playing the Game

**User:** `!trivia next`

**Bot:**
```
🧠 Trivia Question

What is the name of the central planet in Twilight Imperium?

Use !trivia answer <your_answer> to respond
```

---

**User:** `!trivia answer Mecatol Rex`

**Bot:** `🎉 Correct! The answer was: Mecatol Rex`

---

**Another User:** `!trivia answer mecatol rex`

**Bot:** `🎉 Correct! The answer was: Mecatol Rex`

---

**Third User:** `!trivia answer Arborec`

**Bot:** `❌ Incorrect. The correct answer was: Mecatol Rex`

---

## Checking Scores

**User:** `!trivia scores`

**Bot:**
```
**Trivia Scores:**
1. <@123456789>: 1/1 correct
2. <@987654321>: 1/1 correct
3. <@555666777>: 0/1 correct
```

---

## Adding Custom Questions

**User:** `!trivia add Which faction starts with 2 War Suns? | The Embers of Muaat | factions`

**Bot:** `Question added successfully! Category: factions`

---

## Listing Questions

**User:** `!trivia list factions`

**Bot:**
```
**Available Questions (3 total):**
• Which faction has the ability to build War Suns without owning the technology? (Category: factions)
• Which faction starts the game with 2 War Suns? (Category: factions)
• Which faction has the racial ability called 'Fragile'? (Category: factions)
```

---

## Advanced Features

**User:** `!trivia next`

**Bot:**
```
🧠 Trivia Question

How many victory points are needed to win a standard game?

Use !trivia answer <your_answer> to respond
```

**User:** `!trivia answer 10`

**Bot:** `🎉 Correct! The answer was: 10`

---

## Session Management

**User:** `!trivia stop`

**Bot:** `Trivia session stopped.`

---

## Error Handling Examples

**User (not session creator):** `!trivia stop`

**Bot:** `Only the session creator can stop the trivia session.`

---

**User:** `!trivia answer 5`
*(when no active question)*

**Bot:** `No active question found in this channel.`

---

**User:** `!trivia add Too short? | Yes`

**Bot:** `Question must be at least 10 characters long.`

---

## Privacy Feature

The bot encourages users to create temporary channels or threads to keep trivia answers private and non-searchable, addressing the original requirement to "put this in a temporary channel so answers are not searchable."