package com.mycoach.app.ui.clients

import android.app.AlertDialog
import android.os.Bundle
import android.view.*
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.mycoach.app.R
import com.mycoach.app.databinding.FragmentClientsBinding
import com.mycoach.app.models.Client
import com.mycoach.app.models.ClientRequest

class ClientsFragment : Fragment() {

    private var _binding: FragmentClientsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ClientsViewModel by viewModels()
    private val adapter = ClientsAdapter(
        onEdit = { client -> showClientDialog(client) },
        onDelete = { client ->
            MaterialAlertDialogBuilder(requireContext())
                .setTitle("Supprimer ${client.name} ?")
                .setMessage("Cette action est irréversible.")
                .setPositiveButton("Supprimer") { _, _ -> viewModel.delete(client.id) }
                .setNegativeButton("Annuler", null)
                .show()
        }
    )

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentClientsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.recyclerView.layoutManager = LinearLayoutManager(context)
        binding.recyclerView.adapter = adapter

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.load()
        }

        binding.fab.setOnClickListener { showClientDialog(null) }

        viewModel.loading.observe(viewLifecycleOwner) {
            binding.progressBar.visibility = if (it) View.VISIBLE else View.GONE
            if (!it) binding.swipeRefresh.isRefreshing = false
        }

        viewModel.error.observe(viewLifecycleOwner) { err ->
            if (err != null) Toast.makeText(context, err, Toast.LENGTH_LONG).show()
        }

        viewModel.clients.observe(viewLifecycleOwner) { clients ->
            adapter.submitList(clients)
            binding.tvEmpty.visibility = if (clients.isEmpty()) View.VISIBLE else View.GONE
            binding.tvEmpty.text = getString(R.string.no_clients)
        }

        viewModel.load()
    }

    private fun showClientDialog(client: Client?) {
        val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_client, null)
        val etName  = dialogView.findViewById<TextInputEditText>(R.id.etName)
        val etEmail = dialogView.findViewById<TextInputEditText>(R.id.etEmail)
        val etPhone = dialogView.findViewById<TextInputEditText>(R.id.etPhone)
        val etRate  = dialogView.findViewById<TextInputEditText>(R.id.etRate)
        val etNotes = dialogView.findViewById<TextInputEditText>(R.id.etNotes)

        client?.let {
            etName.setText(it.name)
            etEmail.setText(it.email ?: "")
            etPhone.setText(it.phone ?: "")
            etRate.setText(if (it.hourlyRate > 0) it.hourlyRate.toString() else "")
            etNotes.setText(it.notes ?: "")
        }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle(if (client == null) "Nouveau client" else "Modifier ${client.name}")
            .setView(dialogView)
            .setPositiveButton(getString(R.string.save)) { _, _ ->
                val name = etName.text.toString().trim()
                if (name.isEmpty()) { Toast.makeText(context, getString(R.string.error_name_required), Toast.LENGTH_SHORT).show(); return@setPositiveButton }
                viewModel.save(
                    client?.id,
                    ClientRequest(
                        name = name,
                        email = etEmail.text.toString().ifBlank { null },
                        phone = etPhone.text.toString().ifBlank { null },
                        hourlyRate = etRate.text.toString().toDoubleOrNull() ?: 0.0,
                        notes = etNotes.text.toString().ifBlank { null }
                    )
                )
            }
            .setNegativeButton(getString(R.string.cancel), null)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
