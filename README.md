A simple Telegram bot that helps friend groups stop making vague plans and actually meet up. Built entirely in Python as a self-directed learning project.

The bot collects home addresses and availability from group members, then calculates the fairest meeting point by equalising commute times across all users using variance minimisation rather than a simple geographic midpoint. 

Availability is parsed from natural language inputs using regex. It then suggests nearby venues via the Google Places API, filtered by category and free vs paid. Group members can also suggest their own venues, with the bot selecting the fairest option based on commute time equalisation across the group.

Built with Python, Google Maps Distance Matrix API, Google Places API, Geocoding API, and the Telegram Bot API. Deployed on Railway.

Still WIP, with more functions and better suggestion system in the works
