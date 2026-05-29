# Build stage: install Hugo and build the site
FROM hugomods/hugo:exts-0.162.1 AS builder

WORKDIR /src

# Copy the entire site source
COPY . .

# Initialize git submodules (Blowfish theme)
RUN git init && git submodule update --init --recursive

# Build the site
RUN hugo --gc --minify

# Serve stage: use Caddy to serve static files
FROM caddy:2-alpine

COPY --from=builder /src/public /srv

# Railway provides PORT env var
CMD ["caddy", "file-server", "--root", "/srv", "--listen", ":${PORT:-80}"]
