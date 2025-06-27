import { useEffect, useState } from "react"
import { deleteHospital, getHospitals } from "../services/ApiService"
import AddHospital from "./AddHospital"
import Navigation from "./Navigation"

const HospitalList = () => {
    const [hospitals, setHospitals] = useState([])
    const [showAddHospital, setShowAddHospital] = useState(false)

    useEffect(() => {
        let mount = true
        getHospitals()
            .then(res => {
                console.log("Response from api ", res)
                setHospitals(res)
                return() => mount = false
            })
    }, [])

    const handleDeleteBtn = (id) => {
        deleteHospital(id)
            .then(() => setHospitals(hospitals.filter(h=> h.hospital_id !== id)))
    }

    const handleCancelBtn = () => {
        setShowAddHospital(false);
        getHospitals()
            .then(res => {
                console.log("Response from api ", res)
                setHospitals(res)
            })
    }

    return (
        <div>
            <Navigation currentPage="hospitals" />
            <div className="container mt-4">
                <h3>Hospital List</h3>
                <table className="table table-striped table-hover table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Address</th>
                            <th scope="col">Phone</th>
                            <th scope="col">Email</th>
                            <th scope="col">Capacity</th>
                            <th scope="col">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {hospitals.map(hospital => 
                            <tr key={hospital.hospital_id}>
                                <td>{hospital.name}</td>
                                <td>{hospital.address}</td>
                                <td>{hospital.phone}</td>
                                <td>{hospital.email || 'N/A'}</td>
                                <td>{hospital.capacity}</td>
                                <td>
                                    <button className="btn btn-danger" onClick={() => handleDeleteBtn(hospital.hospital_id)}>Delete</button>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
                <br />
                <button className="btn btn-success" onClick={()=>setShowAddHospital(!showAddHospital)}>Add New Hospital</button>
                <br />
                <br />
                {showAddHospital && <AddHospital handleCancelBtn={handleCancelBtn} />}
            </div>
        </div>
    )
}
export default HospitalList 