use crate::primitives::attribute::{Attributive, InnerAttributes};
use crate::primitives::{Attribute, BBox};
use pyo3::{pyclass, pymethods, Py, PyAny};
use rkyv::{with::Skip, Archive, Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[pyclass]
#[derive(Archive, Deserialize, Serialize, Debug, PartialEq, Clone)]
#[archive(check_bytes)]
pub struct ParentObject {
    #[pyo3(get, set)]
    pub id: i64,
    #[pyo3(get, set)]
    pub creator: String,
    #[pyo3(get, set)]
    pub label: String,
}

#[pymethods]
impl ParentObject {
    #[classattr]
    const __hash__: Option<Py<PyAny>> = None;

    fn __repr__(&self) -> String {
        format!("{self:?}")
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    #[new]
    pub fn new(id: i64, creator: String, label: String) -> Self {
        Self { id, creator, label }
    }
}

#[pyclass]
#[derive(Debug, Clone, PartialEq)]
pub enum Modification {
    Id,
    Creator,
    Label,
    BoundingBox,
    Attributes,
    Confidence,
    Parent,
    TrackId,
}

#[derive(Archive, Deserialize, Serialize, Debug, PartialEq, Clone, derive_builder::Builder)]
#[archive(check_bytes)]
pub struct InnerObject {
    pub id: i64,
    pub creator: String,
    pub label: String,
    pub bbox: BBox,
    pub attributes: HashMap<(String, String), Attribute>,
    pub confidence: Option<f64>,
    pub parent: Option<ParentObject>,
    pub track_id: Option<i64>,
    #[with(Skip)]
    pub modifications: Vec<Modification>,
}

impl InnerAttributes for InnerObject {
    fn get_attributes_ref(&self) -> &HashMap<(String, String), Attribute> {
        &self.attributes
    }

    fn get_attributes_ref_mut(&mut self) -> &mut HashMap<(String, String), Attribute> {
        &mut self.attributes
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct Object {
    pub(crate) inner: Arc<Mutex<InnerObject>>,
}

impl Attributive<InnerObject> for Object {
    fn get_inner(&self) -> Arc<Mutex<InnerObject>> {
        self.inner.clone()
    }
}

impl Object {
    #[cfg(test)]
    pub(crate) fn from_inner_object(object: InnerObject) -> Self {
        Self {
            inner: Arc::new(Mutex::new(object)),
        }
    }

    pub(crate) fn from_arc_inner_object(object: Arc<Mutex<InnerObject>>) -> Self {
        Self { inner: object }
    }
}

#[pymethods]
impl Object {
    #[classattr]
    const __hash__: Option<Py<PyAny>> = None;

    fn __repr__(&self) -> String {
        format!("{:#?}", self.inner.lock().unwrap())
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    #[allow(clippy::too_many_arguments)]
    #[new]
    pub fn new(
        id: i64,
        creator: String,
        label: String,
        bbox: BBox,
        attributes: HashMap<(String, String), Attribute>,
        confidence: Option<f64>,
        parent: Option<ParentObject>,
        track_id: Option<i64>,
    ) -> Self {
        let object = InnerObject {
            id,
            creator,
            label,
            bbox,
            attributes,
            confidence,
            parent,
            track_id,
            modifications: Vec::default(),
        };
        Self {
            inner: Arc::new(Mutex::new(object)),
        }
    }

    #[getter]
    pub fn get_track_id(&self) -> Option<i64> {
        let object = self.inner.lock().unwrap();
        object.track_id
    }

    #[getter]
    pub fn get_id(&self) -> i64 {
        self.inner.lock().unwrap().id
    }

    #[getter]
    pub fn get_creator(&self) -> String {
        self.inner.lock().unwrap().creator.clone()
    }

    #[getter]
    pub fn get_label(&self) -> String {
        self.inner.lock().unwrap().label.clone()
    }

    #[getter]
    pub fn get_bbox(&self) -> crate::primitives::BBox {
        self.inner.lock().unwrap().bbox.clone()
    }

    #[getter]
    pub fn get_confidence(&self) -> Option<f64> {
        let object = self.inner.lock().unwrap();
        object.confidence
    }

    #[getter]
    pub fn get_parent(&self) -> Option<ParentObject> {
        let object = self.inner.lock().unwrap();
        object.parent.clone()
    }

    #[setter]
    pub fn set_track_id(&mut self, track_id: Option<i64>) {
        let mut object = self.inner.lock().unwrap();
        object.track_id = track_id;
        object.modifications.push(Modification::TrackId);
    }

    #[setter]
    pub fn set_id(&mut self, id: i64) {
        let mut object = self.inner.lock().unwrap();
        object.id = id;
        object.modifications.push(Modification::Id);
    }

    #[setter]
    pub fn set_creator(&mut self, creator: String) {
        let mut object = self.inner.lock().unwrap();
        object.creator = creator;
        object.modifications.push(Modification::Creator);
    }

    #[setter]
    pub fn set_label(&mut self, label: String) {
        let mut object = self.inner.lock().unwrap();
        object.label = label;
        object.modifications.push(Modification::Label);
    }

    #[setter]
    pub fn set_bbox(&mut self, bbox: BBox) {
        let mut object = self.inner.lock().unwrap();
        object.bbox = bbox;
        object.modifications.push(Modification::BoundingBox);
    }

    #[setter]
    pub fn set_confidence(&mut self, confidence: Option<f64>) {
        let mut object = self.inner.lock().unwrap();
        object.confidence = confidence;
        object.modifications.push(Modification::Confidence);
    }

    #[setter]
    pub fn set_parent(&mut self, parent: Option<ParentObject>) {
        let mut object = self.inner.lock().unwrap();
        object.parent = parent;
        object.modifications.push(Modification::Parent);
    }

    #[getter]
    pub fn attributes(&self) -> Vec<(String, String)> {
        self.inner_attributes()
    }

    pub fn get_attribute(&self, creator: String, name: String) -> Option<Attribute> {
        self.inner_get_attribute(creator, name)
    }

    pub fn delete_attribute(&mut self, creator: String, name: String) -> Option<Attribute> {
        match self.inner_get_attribute(creator, name) {
            Some(attribute) => {
                let mut object = self.inner.lock().unwrap();
                object.modifications.push(Modification::Attributes);
                Some(attribute)
            }
            None => None,
        }
    }

    pub fn set_attribute(&mut self, attribute: Attribute) -> Option<Attribute> {
        {
            let mut object = self.inner.lock().unwrap();
            object.modifications.push(Modification::Attributes);
        }
        self.inner_set_attribute(attribute)
    }

    pub fn clear_attributes(&mut self) {
        {
            let mut object = self.inner.lock().unwrap();
            object.modifications.push(Modification::Attributes);
        }
        self.inner_clear_attributes()
    }

    #[pyo3(signature = (negated=false, creator=None, names=vec![]))]
    pub fn delete_attributes(
        &mut self,
        negated: bool,
        creator: Option<String>,
        names: Vec<String>,
    ) {
        {
            let mut object = self.inner.lock().unwrap();
            object.modifications.push(Modification::Attributes);
        }
        self.inner_delete_attributes(negated, creator, names)
    }

    pub fn find_attributes(
        &self,
        creator: Option<String>,
        name: Option<String>,
        hint: Option<String>,
    ) -> Vec<(String, String)> {
        self.inner_find_attributes(creator, name, hint)
    }

    pub fn take_modifications(&self) -> Vec<Modification> {
        let mut object = self.inner.lock().unwrap();
        std::mem::take(&mut object.modifications)
    }
}

#[cfg(test)]
mod tests {
    use crate::primitives::message::video::object::InnerObjectBuilder;
    use crate::primitives::{AttributeBuilder, BBox, Modification, Object, Value};

    fn get_object() -> Object {
        Object::from_inner_object(
            InnerObjectBuilder::default()
                .id(1)
                .track_id(None)
                .modifications(vec![])
                .creator("model".to_string())
                .label("label".to_string())
                .bbox(BBox::new(0.0, 0.0, 1.0, 1.0, None))
                .confidence(Some(0.5))
                .attributes(
                    vec![
                        AttributeBuilder::default()
                            .creator("creator".to_string())
                            .name("name".to_string())
                            .values(vec![Value::string("value".to_string(), None)])
                            .hint(None)
                            .build()
                            .unwrap(),
                        AttributeBuilder::default()
                            .creator("creator".to_string())
                            .name("name2".to_string())
                            .values(vec![Value::string("value2".to_string(), None)])
                            .hint(None)
                            .build()
                            .unwrap(),
                        AttributeBuilder::default()
                            .creator("creator2".to_string())
                            .name("name".to_string())
                            .values(vec![Value::string("value".to_string(), None)])
                            .hint(None)
                            .build()
                            .unwrap(),
                    ]
                    .into_iter()
                    .map(|a| ((a.creator.clone(), a.name.clone()), a))
                    .collect(),
                )
                .parent(None)
                .build()
                .unwrap(),
        )
    }

    #[test]
    fn test_delete_attributes() {
        pyo3::prepare_freethreaded_python();

        let mut t = get_object();
        t.delete_attributes(false, None, vec![]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 3);

        let mut t = get_object();
        t.delete_attributes(true, None, vec![]);
        assert!(t.inner.lock().unwrap().attributes.is_empty());

        let mut t = get_object();
        t.delete_attributes(false, Some("creator".to_string()), vec![]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 1);

        let mut t = get_object();
        t.delete_attributes(true, Some("creator".to_string()), vec![]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 2);

        let mut t = get_object();
        t.delete_attributes(false, None, vec!["name".to_string()]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 1);

        let mut t = get_object();
        t.delete_attributes(true, None, vec!["name".to_string()]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 2);

        let mut t = get_object();
        t.delete_attributes(false, None, vec!["name".to_string(), "name2".to_string()]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 0);

        let mut t = get_object();
        t.delete_attributes(true, None, vec!["name".to_string(), "name2".to_string()]);
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 3);

        let mut t = get_object();
        t.delete_attributes(
            false,
            Some("creator".to_string()),
            vec!["name".to_string(), "name2".to_string()],
        );
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 1);

        assert_eq!(
            &t.inner.lock().unwrap().attributes[&("creator2".to_string(), "name".to_string())],
            &AttributeBuilder::default()
                .creator("creator2".to_string())
                .name("name".to_string())
                .values(vec![Value::string("value".to_string(), None)])
                .hint(None)
                .build()
                .unwrap()
        );

        let mut t = get_object();
        t.delete_attributes(
            true,
            Some("creator".to_string()),
            vec!["name".to_string(), "name2".to_string()],
        );
        assert_eq!(t.inner.lock().unwrap().attributes.len(), 2);
    }

    #[test]
    fn test_modifications() {
        let mut t = get_object();
        t.set_label("label2".to_string());
        assert_eq!(t.take_modifications(), vec![Modification::Label]);
        assert_eq!(t.take_modifications(), vec![]);

        t.set_bbox(BBox::new(0.0, 0.0, 1.0, 1.0, None));
        t.clear_attributes();
        assert_eq!(
            t.take_modifications(),
            vec![Modification::BoundingBox, Modification::Attributes]
        );
        assert_eq!(t.take_modifications(), vec![]);
    }
}
