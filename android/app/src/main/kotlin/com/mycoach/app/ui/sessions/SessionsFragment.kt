package com.mycoach.app.ui.sessions
import android.os.Bundle; import android.view.*; import android.widget.Toast
import androidx.fragment.app.Fragment; import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.datepicker.MaterialDatePicker
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.mycoach.app.R; import com.mycoach.app.api.ApiClient
import com.mycoach.app.databinding.FragmentSessionsBinding
import com.mycoach.app.models.SessionRequest
import kotlinx.coroutines.*
import java.text.SimpleDateFormat; import java.util.*
class SessionsFragment : Fragment() {
    private var _b: FragmentSessionsBinding? = null; private val b get() = _b!!
    private val vm: SessionsViewModel by viewModels()
    private val adapter = SessionsAdapter { s ->
        MaterialAlertDialogBuilder(requireContext()).setTitle("Supprimer cette séance ?")
            .setPositiveButton("Supprimer") { _,_ -> vm.delete(s.id) }.setNegativeButton("Annuler",null).show()
    }
    override fun onCreateView(i: LayoutInflater, c: ViewGroup?, s: Bundle?): View { _b = FragmentSessionsBinding.inflate(i,c,false); return b.root }
    override fun onViewCreated(v: View, s: Bundle?) {
        super.onViewCreated(v, s)
        b.recyclerView.layoutManager = LinearLayoutManager(context); b.recyclerView.adapter = adapter
        b.swipeRefresh.setOnRefreshListener { vm.load() }
        b.fab.setOnClickListener { showAddDialog() }
        vm.loading.observe(viewLifecycleOwner) { b.progressBar.visibility = if (it) View.VISIBLE else View.GONE; if (!it) b.swipeRefresh.isRefreshing = false }
        vm.error.observe(viewLifecycleOwner) { if (it != null) Toast.makeText(context, it, Toast.LENGTH_LONG).show() }
        vm.sessions.observe(viewLifecycleOwner) { sessions -> adapter.submitList(sessions); b.tvEmpty.visibility = if (sessions.isEmpty()) View.VISIBLE else View.GONE; b.tvEmpty.text = getString(R.string.no_sessions) }
        vm.load()
    }
    private fun showAddDialog() {
        CoroutineScope(Dispatchers.Main).launch {
            val clients = try { withContext(Dispatchers.IO) { ApiClient.service.getClients() } } catch (e: Exception) { Toast.makeText(context, e.message, Toast.LENGTH_SHORT).show(); return@launch }
            if (clients.isEmpty()) { Toast.makeText(context, "Ajoutez d'abord un client", Toast.LENGTH_SHORT).show(); return@launch }
            val names = clients.map { it.name }.toTypedArray()
            var selectedIdx = 0
            val today = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date())
            MaterialAlertDialogBuilder(requireContext()).setTitle("Nouvelle séance").setSingleChoiceItems(names, 0) { _,i -> selectedIdx = i }
                .setPositiveButton("Ajouter (1h aujourd'hui)") { _,_ ->
                    vm.create(SessionRequest(clientId = clients[selectedIdx].id, date = today, durationMinutes = 60, billed = true))
                }.setNegativeButton(getString(R.string.cancel), null).show()
        }
    }
    override fun onDestroyView() { super.onDestroyView(); _b = null }
}
