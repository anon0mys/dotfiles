-- Keymaps carried forward from vimrc

-- Visual paste without overwriting clipboard
vim.keymap.set("v", "p", '"_dP', { desc = "Paste without overwrite" })

-- System clipboard yank
vim.keymap.set({ "n", "v" }, "<leader>y", '"+y', { desc = "Yank to system clipboard" })

-- Typo commands
vim.api.nvim_create_user_command("Q", "q", {})
vim.api.nvim_create_user_command("W", "w", {})
vim.api.nvim_create_user_command("Qall", "qall", {})
