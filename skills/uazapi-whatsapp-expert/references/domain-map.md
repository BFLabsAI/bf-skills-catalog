# Uazapi Domain Map

## Instance And Profile

Core lifecycle and instance configuration:

- `/instance/init`
- `/instance/all`
- `/instance/connect`
- `/instance/disconnect`
- `/instance/status`
- `/instance/updatechatbotsettings`
- `/instance/updateFieldsMap`
- `/instance/updateInstanceName`
- `/instance/updateAdminFields`
- `/instance/proxy`
- `/instance`
- `/instance/privacy`
- `/instance/presence`
- `/profile/name`
- `/profile/image`

## Sending Messages

Outbound delivery and interactive content:

- `/send/text`
- `/send/media`
- `/send/contact`
- `/send/location`
- `/message/presence`
- `/send/status`
- `/send/menu`
- `/send/carousel`
- `/send/location-button`
- `/send/request-payment`
- `/send/pix-button`

## Message Operations

Read or mutate existing messages:

- `/message/download`
- `/message/find`
- `/message/markread`
- `/message/react`
- `/message/delete`
- `/message/edit`

## Groups And Communities

Group and community management:

- `/group/create`
- `/group/info`
- `/group/inviteInfo`
- `/group/join`
- `/group/leave`
- `/group/list`
- `/group/resetInviteCode`
- `/group/updateAnnounce`
- `/group/updateDescription`
- `/group/updateImage`
- `/group/updateLocked`
- `/group/updateName`
- `/group/updateParticipants`
- `/community/create`
- `/community/editgroups`

## Events And Real-Time

Inbound event delivery:

- `/webhook`
- `/globalwebhook`
- `/sse`

Notable differences:

- `/webhook` is instance-scoped
- `/globalwebhook` is admin-scoped
- `/sse` authenticates with query params instead of header security

## AI And Chatbot Platform

Agent and automation surface:

- `/agent/edit`
- `/agent/list`
- `/trigger/edit`
- `/trigger/list`
- `/knowledge/edit`
- `/knowledge/list`
- `/function/edit`
- `/function/list`

## Campaigns

Bulk messaging:

- `/sender/simple`
- `/sender/advanced`
- `/sender/edit`
- `/sender/cleardone`
- `/sender/clearall`
- `/sender/listfolders`
- `/sender/listmessages`

## Chats, Contacts, Labels, Calls

Conversation and CRM-style operations:

- `/chat/block`
- `/chat/blocklist`
- `/chat/labels`
- `/chat/delete`
- `/chat/archive`
- `/chat/read`
- `/chat/mute`
- `/chat/pin`
- `/chat/find`
- `/chat/editLead`
- `/contacts`
- `/contacts/list`
- `/contact/add`
- `/contact/remove`
- `/chat/details`
- `/chat/check`
- `/label/edit`
- `/labels`
- `/quickreply/edit`
- `/quickreply/showall`
- `/call/make`
- `/call/reject`

## Integrations And Business

External integration and business features:

- `/chatwoot/config`
- `/business/get/profile`
- `/business/get/categories`
- `/business/update/profile`
- `/business/catalog/list`
- `/business/catalog/info`
- `/business/catalog/delete`
- `/business/catalog/show`
- `/business/catalog/hide`

## Selection Heuristic

Choose the domain first, then open only the relevant paths in the full OpenAPI file. Avoid loading the entire spec unless the task genuinely spans multiple domains.
