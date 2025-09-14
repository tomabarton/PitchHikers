FROM alpine
COPY . /
CMD ["stream run PitchHikers.py"]