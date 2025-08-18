import discord
import logging
from discord.ext import commands
from sqlalchemy import Engine
from typing import Optional
from . import trivialogic
from ..typing import *


class Trivia(commands.Cog):
    """Cog containing trivia game commands."""

    def __init__(self, bot: commands.Bot, engine: Engine) -> None:
        self.bot = bot
        self.logic = trivialogic.TriviaLogic(bot, engine)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logging.info("Trivia cog loaded")

    def __string_from_string_result(self, s: Result[str]) -> str:
        match s:
            case Ok(a):
                return a
            case Err(b):
                return b

    @commands.group(invoke_without_command=True)
    async def trivia(self, ctx: commands.Context) -> None:
        """Trivia game commands. Use !trivia start to begin a new game."""
        await ctx.send(
            "**Trivia Game Commands:**\n"
            "`!trivia start` - Start a new trivia session\n"
            "`!trivia stop` - Stop the current trivia session\n"
            "`!trivia next` - Get the next question\n"
            "`!trivia answer <your_answer>` - Answer the current question\n"
            "`!trivia scores` - Show current scores\n"
            "`!trivia add <question> | <answer> [| category]` - Add a new question\n"
            "`!trivia list [category]` - List available questions\n"
            "\n*Tip: Consider using a temporary channel for trivia to keep answers private!*"
        )

    @trivia.command()
    async def start(self, ctx: commands.Context) -> None:
        """Start a new trivia session in this channel."""
        # Check if this is a temporary channel or suggest creating one
        if not isinstance(ctx.channel, discord.Thread):
            embed = discord.Embed(
                title="💡 Tip: Use a Temporary Channel",
                description=(
                    "For the best trivia experience, consider creating a temporary channel or thread "
                    "so that answers aren't searchable later. You can create a thread by right-clicking "
                    "this message and selecting 'Create Thread'."
                ),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

        result = self.logic.create_session(ctx.channel.id, ctx.author.id)
        await ctx.send(self.__string_from_string_result(result))

    @trivia.command()
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the current trivia session."""
        result = self.logic.stop_session(ctx.channel.id, ctx.author.id)
        await ctx.send(self.__string_from_string_result(result))

    @trivia.command()
    async def next(self, ctx: commands.Context) -> None:
        """Get the next trivia question."""
        result = self.logic.next_question(ctx.channel.id)
        
        match result:
            case Ok((question_text, question_id)):
                embed = discord.Embed(
                    title="🧠 Trivia Question",
                    description=question_text,
                    color=discord.Color.green()
                )
                embed.set_footer(text="Use !trivia answer <your_answer> to respond")
                await ctx.send(embed=embed)
            case Err(error):
                await ctx.send(error)

    @trivia.command()
    async def answer(self, ctx: commands.Context, *, answer: str) -> None:
        """Answer the current trivia question."""
        if not answer.strip():
            await ctx.send("Please provide an answer.")
            return
            
        result = self.logic.answer_question(ctx.channel.id, ctx.author.id, answer)
        await ctx.send(self.__string_from_string_result(result))

    @trivia.command()
    async def scores(self, ctx: commands.Context) -> None:
        """Show current trivia scores."""
        result = self.logic.get_scores(ctx.channel.id)
        await ctx.send(self.__string_from_string_result(result))

    @trivia.command()
    async def add(self, ctx: commands.Context, *, content: str) -> None:
        """Add a new trivia question. Format: question | answer | category (optional)"""
        parts = [part.strip() for part in content.split('|')]
        
        if len(parts) < 2:
            await ctx.send(
                "Invalid format. Use: `!trivia add <question> | <answer> | [category]`\n"
                "Example: `!trivia add What is the capital of France? | Paris | Geography`"
            )
            return
        
        question_text = parts[0]
        answer = parts[1]
        category = parts[2] if len(parts) > 2 else "custom"
        
        result = self.logic.add_question(ctx.author.id, question_text, answer, category)
        await ctx.send(self.__string_from_string_result(result))

    @trivia.command(name="list")
    async def list_questions(self, ctx: commands.Context, category: Optional[str] = None) -> None:
        """List available trivia questions, optionally filtered by category."""
        result = self.logic.list_questions(category)
        await ctx.send(self.__string_from_string_result(result))