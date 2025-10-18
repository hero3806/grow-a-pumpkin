import asyncio
import os
import random
import traceback
import discord
from discord.ext import commands

from libs import json
from libs.resourcefinder import Resource
from structs import messages

class Listeners(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.chance = 5
        self.message_count = 0
        self.pumpkin_role_id = 1428982714199179336
        self.current_top_user = None

    def _get_age_path(self):
        return "storage/json/age.json"

    def get_age_data(self):
        return json.get_json(self._get_age_path()) or {}
        
    def getImageAsDiscordFile(self, path):
        with open(path, "rb") as file:
            filename = os.path.basename(path)
            return discord.File(file, filename=f"{filename}.png"), filename
            
    async def update_top_role(self, guild: discord.Guild):
        data = self.get_age_data()
        if not data:
            return
        
        sorted_data = sorted(data.items(), key=lambda x: x[1]["age"], reverse=True)
        top_user_id = int(sorted_data[0][0])
        top_member = guild.get_member(top_user_id)
        
        if not top_member:
            return
        
        role = guild.get_role(self.pumpkin_role_id)
        if not role:
            print(f"[Pumpkin Warning] Role ID {self.pumpkin_role_id} not found in guild {guild.name}")
            return
        
        if self.current_top_user != top_user_id:
            # Remove the role from the previous holder (if any)
            if self.current_top_user:
                prev_member = guild.get_member(self.current_top_user)
                if prev_member and role in prev_member.roles:
                    await prev_member.remove_roles(role, reason="No longer #1 on Pumpkin Leaderboard")
            
            # Give the role to the new #1
            await top_member.add_roles(role, reason="Now #1 on Pumpkin Leaderboard")
            self.current_top_user = top_user_id
            dm_channel = await top_member.create_dm()
            
            if dm_channel:
                await dm_channel.send(embed=messages.success("You've reached the #1 spot!\n:first_place: Congrats! You've been granted the `@Pumpkin Pumper` Role!"))

                
    @commands.hybrid_command(
        name="leaderboard",
        description="Shows the top pumpkin growers!"
    )
    async def leaderboard(self, ctx: commands.Context):
        data = self.get_age_data()

        if not data:
            await ctx.send(embed=messages.error("No pumpkins have been grown yet!"))
            return

        # Sort users by age in descending order
        sorted_data = sorted(data.items(), key=lambda x: x[1]["age"], reverse=True)

        # Limit to top 10
        top_10 = sorted_data[:10]

        desc = ""
        for i, (user_id, info) in enumerate(top_10, start=1):
            user = ctx.guild.get_member(int(user_id))
            username = user.name if user else f"Unknown ({user_id})"
            
            if i==1:
                correctedIndex = f":first_place: {i}"
            elif i==2:
                correctedIndex = f":second_place: {i}"
            elif i==3:
                correctedIndex = f":third_place: {i}"
            else:
                correctedIndex = i
            desc += f"**{correctedIndex}.** — `{username}:` 🌱 **{info['age']}  {"year" if info["age"] == 1 else "years"}**\n"

        embed = messages.success(" Pumpkin Leaderboard 🎃")
        embed.description += "\nRace to the 1st place to win the <@&1428982714199179336> role! [LIMITED TIME ONLY]"
        embed.description += "\n\n"+desc
        embed.set_footer(text="Keep messaging to grow your pumpkin!")

        await ctx.send(embed=embed)
        
    @commands.hybrid_command(
        name="age",
        description="Gets a User's Pumpkin age!"
    )
    async def age(self, ctx:commands.Context, user:discord.Member|discord.User = None):
        if not user:
            user = ctx.author
            
        user_id = str(user.id)
        data = self.get_age_data()

        if user_id in data:
            
            sorted_data = sorted(data.items(), key=lambda x: x[1]["age"], reverse=True)
            rank = next((i + 1 for i, (uid, _) in enumerate(sorted_data) if uid == user_id), None)
            
            image, filename = self.getImageAsDiscordFile(Resource.get_image("pumpkin"))
            
            embed = messages.success(f"**{user.name}'s pumpkin is {data[user_id]['age']} years old!**")
            embed.set_footer(text="Keep messaging to grow your pumpkin!")
            embed.set_thumbnail(url=f"attachment://{filename}.png")
            
            if rank:
                embed.description += f"\n:medal: Leaderboard Rank: {rank}"
            await ctx.send(embed=embed, file=image)
        else:
            await ctx.send(embed=messages.error("User does not have a pumpkin yet or it is inaccesible!"))
        
        
    @commands.command()
    @commands.is_owner()
    async def prc(self, ctx:commands.Context, num:int):
        if num > 100:
            num = 100
        
        self.chance = num
        await ctx.send(f"[DEBUG] chance = {num}%")
        
    @commands.command()
    @commands.is_owner()
    async def msg_cnt(self, ctx:commands.Context, num:int):
        self.message_count = num
        await ctx.send(f"[DEBUG] message_count = {num}")
        
    # Example command
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        if message.guild.id != 1415362113056018546: return
        
        self.message_count += 1
        if self.message_count == 150:
            self.chance *= 10
            embed = messages.success("LUCK BOOST!")
            embed.description = "### <:luck:1428973560432427081> 10X LUCK ACTIVE!\n`Duration:` 2m"
            await message.channel.send(embed=embed)
            
            async def reset_luck():
                await asyncio.sleep(120)  # 2 minutes
                self.chance //= 10
                self.message_count = 0  # optional: reset message count to start over
                end_embed = messages.error("LUCK BOOST ENDED!")
                end_embed.description = "### :no_entry_sign: 10X LUCK EXPIRED!"
                await message.channel.send(embed=end_embed)

            asyncio.create_task(reset_luck())
            
        if random.randrange(100) < self.chance:
            data = self.get_age_data()
            
            user_id = str(message.author.id)
            if user_id not in data:
                data[user_id] = {"age": 0}
                
            data[user_id]["age"] += 1
                
            msg = await message.reply(f"Your pumpkin grew up! :jack_o_lantern: \n**Age: {data[user_id]["age"]}**\n-# • Keep messaging to grow your pumpkin!", mention_author=False)
            await asyncio.sleep(4)
            await msg.delete()
            
            path = self._get_age_path()
            json.dump_json(path, data)
            
            await self.update_top_role(message.guild)
            return
                
    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        await ctx.send(embed=messages.error(error))
        
        traceback.print_exception(type(error), error, error.__traceback__)
            

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))