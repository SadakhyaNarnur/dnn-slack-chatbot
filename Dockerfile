FROM --platform=$BUILDPLATFORM python:3.11 AS builder

ENV SLACK_TOKEN_ xoxb-6659138368100-6672589994658-IIbpCY32UyWtr0VPDCwGFAsb
ENV SIGNING_SECRET_ c89e2cb12be8c6b870e1d8a170bafa81
ENV HOOKUP_URL https://hooks.slack.com/services/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

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY botapp /app

# EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["/app/tutorial.py"]