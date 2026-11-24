# Control switching handoff — November24

Process execution recovered; KiCad10.0.6 and native exports work. Pin/preservation checks and Excellon drill-delta checks pass. 55 completed simulation runs have checked input/deck provenance and refinement receipts. Q1/Q2 and D333/D342 are adopted; U3 TPS3890 remains a candidate with explicit timing/edge/carrier holds. See review.md and results/adoption.json. The guarded one-time native mutation factories must not be rerun.

Source, board plan and component coverage are synchronized for this correction; R215 was added to the board plan to match the earlier verified native integration. The Control board still has84 unconnected items and13 existing DRC findings. No fabrication release or full populated fit is claimed.

FB-117 keeps actual IC sockets as the default and permits a documented device-specific exception when socketing materially harms operation. No exception adopted. All tubes retain sockets. Next: qualify reset/carrier/edge conditioning and actual rail collapse; exact sourceable sockets/contacts and auxiliary magnetics; populated three-board assembly including socket extraction and independent rear removal. Actual drill dimensions deferredNovember25.

Review and stage this owned work only; existing mechanical, lettering, feedback and other dirty edits remain separate. The current checkpoint needs final ICM/catalog checks and Git commit/push; record the successful commit in the user-facing handoff after verification.
