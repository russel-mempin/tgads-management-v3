import { defineStore } from "pinia";
import { ref } from "vue";
import { getForReviewCount } from "@/api/forReviews";

export const useForReviewCount = defineStore("ForReviewCounter", () => {
	const count = ref(0)
	const loading = ref(false)

	async function fetchCount() {
		loading.value = true
		try {
			count.value = await getForReviewCount()
		}
		finally {
			loading.value = false
		}
	}

	return {
		count,
		loading,
		fetchCount
	}
})