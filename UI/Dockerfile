FROM node:18.18.0
 
# Set working directory
WORKDIR /usr/src/app
 
# Copy package.json and package-lock.json
COPY package*.json ./
 
# Install dependencies
RUN npm install --legacy-peer-deps

# RUN npm install ajv --legacy-peer-deps
 
# Copy application files
COPY . .
 
# Expose port
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]

